/*
 *	Copyrighted, Research Foundation of SUNY, 1998
 */

#ifndef SEGMENT_H
#define SEGMENT_H
#include "DynamicArray.h"

#include "Grid.h"
#include "LatticeModel.h"
#include "Variation.h"
#include "threshold.h"
#include <cstring>
#include <cuchar>

const float fCAT_0 = 0.0;
const float fCAT_1 = 1.0;
const float fto_be_CAT_0 = 0.3f;
const float fto_be_CAT_1 = 0.7f;
const float fto_be_ESTIMATED_f = 2.0;

const int CAT_0 = 0;
const int CAT_1 = 1;
const int to_be_CAT_0 = 15; //!!!!
const int to_be_CAT_1 = 16;
const int to_be_ESTIMATED_f = 10;

const uc to_be_ESTIMATED = (uc)140;
const uc marked_PORE = (uc)2;
const uc estimated_PORE = (uc)3;
const uc filtered_PORE = (uc)7;
const uc filtered_ROCK = (uc)13;
const uc estimated_ROCK = (uc)16;
const uc marked_ROCK = (uc)20;
const uc marked_exterior = (uc)130;

struct DataDescription {
  int W;
  int H;
  int D;
};

struct KrigingSettings {
  KrigingSettings()
      : Radius(3), VarMethod('m'), OutFormat('v'), CorMethod('i'), nLlabels(2) {
    VarMethod = 'm';
    CorMethod = 'i';
    OutFormat = 'v';
  }
  char VarMethod;
  char CorMethod;
  char DataCorMethod;
  char OutFormat;
  int Radius;
  int SegMethod;
  int nLlabels;
  ThresholdSettings Theshold;
};

template <class T = int, class container_type = std::vector<T>, int nDim = 2>
class KrigingProcessor
    : public LatticeModel<T, container_type, nDim> //, public ITestable
{
  using LatticeIterator = typename container_type::iterator;
  using LatticeConstIterator = typename container_type::const_iterator;

public:
  KrigingProcessor(int LabelsCount)
      : LatticeModel<T, container_type, nDim>(
            LabelsCount) //, Undef(LabelsCount), InNB(LabelsCount + 1)
        {};

  void ComputeVriogramBetweenThresholds() {}

  void kriging_2way(const Grid &grid, container_type &data_int,
                    container_type &status, long long unmarked,
                    const Variation &var, const Threshold<T> &met, int radius);

  void correct_weights(double *wgt, size_t n, const Variation &covar,
                       const Point *coord) {
    LogFile::WriteData("kriging.log",
                       "correct_weights(double* wgt, size_t n, const "
                       "Variation& covar, const Point* coord)");
    DynamicArray<long long> index(n);
    int j = 0;
    double avg = 0.0;
    double Cavg = 0.0;
    int i;
    for (i = 0; i < n; ++i) {
      if (wgt[i] < 0.0) {
        avg -= wgt[i];
        Cavg += covar(coord[i].abs());
        index[j++] = i;
      }
    }
    if (j == 0)
      return;

    int n_negative = j;
    avg /= n_negative;
    Cavg /= n_negative;
    double sum = 0.0;
    for (i = 0; i < n; ++i) {
      if (wgt[i] < 0.0)
        wgt[i] = 0.0;
      else if (covar(coord[i].abs()) < Cavg && wgt[i] < avg)
        wgt[i] = 0.0;
      sum += wgt[i];
    }
    for (i = 0; i < n; ++i)
      wgt[i] /= sum;
    LogFile::WriteData("kriging.log", "correct_weights finished");
  }

  void segment(container_type &data, const Grid &grid, const Variation &var,
               Threshold<T> &Thresh, KrigingSettings &sp,
               ThresholdSettings &ts) {
    LogFile::WriteData("kriging.log", "Kriging segment procedure started");

    size_t i;
    int radius;
    int tbc0 = 0;
    int tbc1 = 0;

    if (Thresh.Method != Th_Manual) {
      LogFile::WriteData("kriging.log", "Calc threahold");
      int ImgSize = grid.n_x() * grid.n_y();
      DynamicArray<T> I(ImgSize);
      std::copy(data.begin(), data.begin() + ImgSize, I.begin());
      Thresh.compute_cut_offs(I, grid.n_x(), grid.n_y(), 1); //!!!
    }

    LogFile::WriteData("kriging.log", "Low threshold", +Thresh.Low());
    LogFile::WriteData("kriging.log", "High threshold", +Thresh.High());

    container_type status(data.size());
    for (auto it = status.begin(); it != status.end(); it++)
      *it = 0;
    long long unmarked = mark(data, status, Thresh);
    if (grid.dim() == 2)
      radius = sp.Radius;
    else if (grid.dim() == 3)
      radius = sp.Radius;

    if (Thresh.Low() != Thresh.High()) {
      // median_filter(status,grid,0.6);
      LogFile::WriteData("kriging.log", "kriging_2way");
      kriging_2way(grid, data, status, unmarked, var, Thresh, radius);
      LogFile::WriteData("kriging.log", "Krig_2way finished");
    }
    ///!!!
    // median_filter(status,grid,0.6);
    ts.OutHighThreshold = Thresh.High();
    ts.OutLowThreshold = Thresh.Low();

    auto pi = status.begin();
    auto pd = data.begin();
    for (i = 0; i < status.size(); ++i, ++pi, ++pd) {
      if (*pi == marked_exterior)
        *pd = ext_value(int(0));
      else // if (*pi == marked_PORE)
        *pd = (*pi - to_be_ESTIMATED - 1);
      /*	else if (*pi == marked_ROCK)
                      *pd = CAT_1;
              else if (*pi == filtered_ROCK)
                      *pd = CAT_1;
              else if (*pi == filtered_PORE)
                      *pd = CAT_0;
              else if (*pi == estimated_PORE)
              {
                      *pd = to_be_CAT_0; ++tbc0;
              }
              else if (*pi == estimated_ROCK)
              {
                      *pd = to_be_CAT_1; ++tbc1;
              }*/
    }
    //	cout << tbc0 << " voxels are kriged as pop_0 (VOID)" << endl;
    //	cout << tbc1 << " voxels are kriged as pop_1 (GRAIN)" << endl;
    LogFile::WriteData("kriging.log", "Krig_2way finished");
  }

  void prepare(char method, Grid &grid, Variation &var, Threshold<T> &thr,
               KrigingSettings &sp, ThresholdSettings &ts,
               const DataDescription &dd) {
    LogFile::WriteData("kriging.log",
                       "prepare(char method,	Grid &grid, Variation	&var, "
                       "Threshold<T>	&thr, KrigingSettings &sp, "
                       "ThresholdSettings &ts, const DataDescription &dd)");
    Point L, U;
    int size[3];

    size_t nx, ny, nz; // , nxyz;
    int seg_dim = 2;
    if (dd.D > 1)
      seg_dim = 3;

    int max_lag = 10;
    double unit_lag = 1.0;
    var = Variation(max_lag, unit_lag, V_direction::Horizontal,
                    V_method::classic_semivariogram, Semivariogram,
                    Semivariogram);

    if (method == 'k') {
      var.set_method(sp.VarMethod);
      var.set_direction(sp.CorMethod);
      var.set_type(sp.OutFormat);
    }

    thr.Flatness() = 0.07;
    thr.Method = ts.ThresholdMethod;
    thr.SetManualThresholds(ts.LowThreshold, ts.HighThreshold);
    thr.PeaksCount() = ts.nPeaks;
    thr.Alpha() = ts.alpha;
    thr.Setup(ts);

    nx = dd.W;
    ny = dd.H;
    nz = dd.D;
    L = Point(0.0, 0.0, 0.0);
    if (seg_dim == 3) {
      U = Point((double)nx, (double)ny, (double)nz);
      size[0] = static_cast<int>(nx);
      size[1] = static_cast<int>(ny);
      size[2] = static_cast<int>(nz);
    } else {
      U = Point((double)nx, (double)ny, 0.0);
      size[0] = static_cast<int>(nx);
      size[1] = static_cast<int>(ny);
      size[2] = 1;
    }

    grid.set(seg_dim, L, U, size, 0, 0);
  }

  // extern	"C"
  void krig_driver(char method, container_type &idat, container_type &outdat,
                   const DataDescription &dd, KrigingSettings &sp,
                   ThresholdSettings &ts) {
    LogFile::WriteData("kriging.log",
                       "krig_driver(char method, container_type	&idat, "
                       "container_type &outdat, const DataDescription &dd, "
                       "KrigingSettings &sp, ThresholdSettings &ts)");
    std::ios::sync_with_stdio();
    Grid grid;

    //	FID_POLY   fid_poly;
    Variation var;
    // THRESHOLD  thr;
    // char	uncmpfn[256];
    // char *infn;
    // size_t	infn_len, infn_inct, infn_cmprss;

    // char	*segfn; // , *segfn_base;
    int seg_dim;

    size_t nx, ny, nxy;
    int z_no;

    // int	**bh;
    // int	*bh_count;
    size_t n;

    //	JgrMer	Jmer;

    //	int	*pidat, *ppidat;
    //	uc	*puc;

    //		int	k;
    //		float	vox_len;

    int gmin, gmax;

    Threshold<T> Thresh;
    LogFile::WriteData("kriging.log", "prepare");
    prepare(method, grid, var, Thresh, sp, ts, dd);

    nx = grid.n_x();
    ny = grid.n_y();
    nxy = nx * ny;
    /* This loop does complete 2d kriging segmentation */
    /* For 3d segmentation, all it does is load idat */

    seg_dim = grid.dim();

    gmin = gmax = 0;

    if (seg_dim == 2) {
      krig_dat(method, idat, grid, var, Thresh, sp, ts);
      auto puc = outdat.begin();
      auto pidat = idat.begin();
      for (n = 0; n < nxy; n++, puc++, pidat++) {
        *puc = *pidat;
        /*if (*pidat == ext_value(int(0)))
                *puc = 255;
        else if (*pidat == CAT_0)
        {
                *puc = 0;
        }
        else if (*pidat == CAT_1)
        {
                *puc = 255;
        }*/
      }
    }

    /* 3d segmentation */
    if (seg_dim == 3) {
      LogFile::WriteData("kriging.log", "krig_dat");
      krig_dat(method, idat, grid, var, Thresh, sp, ts /*,&Jmer*/);

      auto pidat = idat.begin();
      auto ppidat = idat.begin();

      DynamicArray<uc> ucdat(nx * ny);
      auto puc = outdat.begin();
      LogFile::WriteData("kriging.log", "Fillong output");
      for (z_no = 0; z_no < grid.n_z(); z_no++, pidat += nxy) {
        ppidat = pidat;
        for (n = 0; n < nxy; n++, puc++, ppidat++) {
          //	if (*ppidat == ext_value(int(0))) *puc = 255;
          //	else if (*ppidat == CAT_0) *puc = 0;
          //	else if (*ppidat == CAT_1) *puc = 255;//1;
          *puc = *ppidat;
        }
      }
    } /**/
  }

  //
  // This function is called for both kriging segmentation and
  // Mardia-Hainsworth segmentation
  //
  void krig_dat(char method, container_type &raw_data, const Grid &grid,
                // const FID_POLY	&fid_poly,
                Variation &var, Threshold<T> &Thresh, KrigingSettings &sp,
                ThresholdSettings &ts //,
  ) {

    double mean, variance;
    //		int		*pfd;

    int seg_dim = grid.dim();
    // size_t	i, z,
    size_t data_size = raw_data.size();
    size_t nx = grid.n_x();
    size_t ny = grid.n_y();
    size_t nz = grid.n_z();
    int nv, ng;
    int min, max;

    // char	varfn[256];
    // char	*holdfn;
    // char	vtype[256];

    size_t nxy = nx * ny;
    DynamicArray<uc> ucdat(nxy);

    if (method == 'k') {
      LogFile::WriteData("kriging.log", "compute variogram");
      // var.compute(raw_data.begin(), grid, 0, 1);
      LogFile::WriteData("kriging.log", "segmentation");
      segment(raw_data, grid, var, Thresh, sp, ts /*,jmer*/);
    }

    container_type &segmented = raw_data;
    data_size = segmented.size();
    auto pseg = segmented.begin();
    nv = ng = 0;
    for (size_t i = 0; i < data_size; i++, pseg++) {
      if (*pseg == CAT_0)
        ++nv;
      else if (*pseg == to_be_CAT_0) {
        *pseg = CAT_0;
        ++nv;
      } else if (*pseg == CAT_1)
        ++ng;
      else if (*pseg == to_be_CAT_1) {
        *pseg = CAT_1;
        ++ng;
      }
    }
    stats_p(segmented.begin(), segmented.end(), min, max, mean, variance);

    // if (method == 'k')
    //{
    //	Variation before = var;
    //	var.compute(segmented.begin(), grid, 0, 1);
    //	if (var.type() == Covariance)
    //		strcpy(vtype, "Covariance");
    //	else
    //		strcpy(vtype, "Semivariogram");

    //}
  }

  long long mark(const container_type &data, container_type &status,
                 Threshold<T> &met) {
    const int ext_value = ::ext_value(int(0));
    auto p = data.begin();

    LogFile::WriteData("kriging.log", "Mark procedure");
    double dp;
    double sum0, sum1, sqsum0, sqsum1;
    // double	mean0, mean1, var0, var1;

    size_t i;
    long long n_0, n_1, n_e;
    size_t size;

    n_0 = n_1 = n_e = 0;
    sum0 = sqsum0 = sum1 = sqsum1 = 0.0;

    size = data.size();
    typename container_type::iterator pi = status.begin();
    int nPhases = met.PhasesCount();
    bool stop = false;
    for (i = 0; i < size; ++i, ++p, ++pi) {
      dp = double(*p);
      int j = 0;
      stop = false;
      while (j < nPhases && !stop) {
        if (dp == ext_value) {
          *pi = marked_exterior;
          stop = true;
        } else if (dp >= met.LowThresholds()[j] - EPS_THINY &&
                   dp <= met.HighThresholds()[j] + EPS_THINY) {
          //	++n_0;
          *pi = to_be_ESTIMATED + 1 + j;
          stop = true;
          //	sum0 += dp;
          //	sqsum0 += dp*dp;
        }
        /*	else if (dp >= met.High())
                {
                        //	++n_1;
                        *pi = to_be_ESTIMATED + nPhases;
                        //	sum1 += dp;
                        //sqsum1 += dp*dp;
                }*/
        else {
          ++n_e;
          *pi = to_be_ESTIMATED;
          // stop = true;
        }
        j++;
      }
    }

    //	mean0 = sum0 / n_0;	var0 = sqsum0 / n_0 - mean0*mean0;
    //	mean1 = sum1 / n_1;	var1 = sqsum1 / n_1 - mean1*mean1;

    // met.mix.sigma0 = sqrt(var0);	met.mix.sigma1 = sqrt(var1);

    //	cout << n_0 << " voxels marked pop_0 (VOID)  mean " << mean0;
    //	cout << " std_dev " << met.mix.sigma0 << endl;
    //	cout << n_1 << " voxels marked pop_1 (GRAIN) mean " << mean1;
    //	cout << " std_dev " << met.mix.sigma1 << endl;

    //	cout << n_e << " voxels (" << 100.0*n_e / (n_0 + n_1 + n_e) << "%)";
    //	cout << " are to be estimated by kriging.\n";
    return n_e;
  }

  void smooth_indicator_function(CDF &cdf, double low, double high) {
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) low",
        low);
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) high",
        high);

    double x0 = cdf.x_0();
    double xn = cdf.x_n();
    double delta = cdf.delta();
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) x0", x0);
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) xn", xn);
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) delta",
        delta);
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) size",
        cdf.size());

    if (low < x0)
      low = x0;
    if (high > xn)
      high = xn;

    double F_low = cdf.F(low);
    double F_high = cdf.F(high);
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) F_low",
        F_low);
    LogFile::WriteData(
        "kriging.log",
        "smooth_indicator_function(CDF& cdf, double low, double high) F_high",
        F_high);
    double x = x0;
    for (diterator p = cdf.begin(); p != cdf.end(); ++p) {
      if (x < low)
        *p = 1.0;
      else if (x < high)
        *p = (F_high - *p) / (F_high - F_low);
      else
        *p = 0.0;
      x += delta;
    }
  }

  double ok_system_setup2(std::vector<double> &mat, size_t n_of_data,
                          const Variation &f, const Point *coord) {
    std::string fname("double ok_system_setup(vector<double> "
                      "&,int,V_Type,const Variation &,const Point *)");

    // setup ordinary kriging system
    // it assumes covariance f, not semivariogram
    // NOTE: In this routine,
    // mat is supposed to be a matrix of (n_of_data+1) by (n_of_data+1)
    // the actual argument passed in may have a bigger memory allocated.
    // Make sure that you correctly use the first (n_of_data+1)x(n_of_data+1)

    if (f.type() != Covariance)
      error("Covariance type is required.", fname);

    size_t cols = n_of_data + 1;
    size_t rows = cols;
    diterator first = mat.begin();

    // setup the matrix

    diterator pm;
    const Point *p = coord;
    const Point *pc;
    for (size_t row = 0; row < n_of_data; ++row, ++p) {
      pc = coord;
      pm = mat.begin() + row * cols;
      for (size_t col = 0; col < row; ++col) { // setup lower triangular part
        double gamma = f(dist(*p, *pc++));
        mat[row * cols + col] = gamma;
        mat[rows * col + row] = gamma;
      }
      mat[row * cols + row] = 0; // diagonal element;
    }
    pm = mat.begin() + n_of_data * cols; // last row
    for (int i = 0; i < n_of_data; ++i) {
      *pm++ = 1.0;
      mat[(i + 1) * cols - 1] = 1;
    }
    *pm = 0.0; // not necessarily mat.end()-1

    return 0.0;
  }

  int set_coord_sphere(int radius, int dim, Point *coord) {

    int n = 0;
    int dist;
    int rsquare = radius * radius;

    if (dim == 2) {
      for (int j = -radius; j <= radius; ++j) {
        for (int i = -radius; i <= radius; ++i) {
          dist = j * j + i * i;
          if (dist > rsquare)
            continue;
          if (j == 0 && i == 0)
            continue;
          coord[n] = Point(i, j, 0);
          ++n;
        }
      }
    } else if (dim == 3) {
      for (int k = -radius; k <= radius; ++k) {
        for (int j = -radius; j <= radius; ++j) {
          for (int i = -radius; i <= radius; ++i) {
            dist = k * k + j * j + i * i;
            if (dist > rsquare)
              continue;
            if (k == 0 && j == 0 && i == 0)
              continue;
            coord[n] = Point(i, j, k);
            ++n;
          }
        }
      }
    }
    return n;
  }

  size_t set_neighbor_sphere(long long w, int radius, const Grid &grid,
                             container_type &status, container_type &data,
                             double *cond_data0, const CDF &cdf0,
                             unsigned char nPhase);
  // {

  // 	int depth = grid.n_z();
  // 	int rows = grid.n_y();
  // 	int cols = grid.n_x();

  // 	const int	z = static_cast<int>(w / (cols*rows));
  // 	const int	y = static_cast<int>((w - z*cols*rows) / cols);
  // 	const int	x = static_cast<int>((w - z*cols*rows) % cols);

  // 	int dim = grid.dim();

  // 	int from_d, to_d;
  // 	if (dim == 2) {
  // 		from_d = 0;
  // 		to_d = 1;
  // 	}
  // 	else if (dim == 3) {
  // 		from_d = z - radius;
  // 		to_d = z + radius + 1;
  // 	}
  // 	const int	from_r = y - radius;
  // 	const int	to_r = y + radius + 1;
  // 	const int	from_c = x - radius;
  // 	const int	to_c = x + radius + 1;

  // 	int rsquare = radius*radius;

  // 	// the ordering should match with that of set_coord_sphere() above
  // 	size_t n = 0;
  // 	for (long long k = from_d; k<to_d; ++k) {
  // 		for (long long j = from_r; j<to_r; ++j) {
  // 			for (long long i = from_c; i<to_c; ++i) {
  // 				if ((k - z)*(k - z) + (j - y)*(j - y) + (i -
  // x)*(i
  // - x)
  // >
  // rsquare) continue; 				if ((k == z) && (j == y)
  // && (i
  // == x)) continue; 				if (k<0
  // || k >= depth || j<0 || j >= rows || i<0 || i >= cols) {
  // cond_data0[n] = 0.5;
  // 				//	cond_data1[n] = 0.5;
  // 				}
  // 				else {
  // 					size_t index = (k*rows + j)*cols + i;
  // 					uc pi = status[index];
  // 					if (pi == marked_exterior) {
  // 						cond_data0[n] = 0.5;
  // 					}
  // 					else if (pi == nPhase-1 /*||
  // pi==filtered_PORE*/)
  // { 						cond_data0[n] =1.0;///!!!!!
  // 					}
  // 					else if (pi == nPhase /*||
  // pi==filtered_ROCK*/)
  // { 						cond_data0[n] = 0.0;//!!!!
  // 					}
  // 					else
  // 					{
  // 						double value = data[index];
  // 						cond_data0[n] = cdf0.F(value);
  // 						//cond_data1[n] = cdf1.F(value);
  // 					}
  // 				}
  // 				++n;
  // 			}
  // 		}
  // 	}
  // 	return n;
  // }
};

#endif
