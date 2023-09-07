#include <unordered_map>
#include <vector>
#include <math.h>
#include <iostream>

template <typename T>
struct VectorHasher
{
   // References:  https://jimmy-shen.medium.com/stl-map-unordered-map-with-a-vector-for-the-key-f30e5f670bae
   //				https://stackoverflow.com/questions/20511347/a-good-hash-function-for-a-vector
   // Should use the same method as boost to generate a hash

   int operator()(const std::vector<T> &vec) const
   {
      std::size_t hash = vec.size();
      for (auto &i : vec)
      {
         hash ^= i + 0x9e3779b9 + (hash << 6) + (hash >> 2);
      }
      return hash;
   }
};

typedef std::size_t index_t;
typedef std::vector<index_t> key_type;
typedef std::unordered_map<key_type, std::vector<index_t>, VectorHasher<index_t>> map_t;

void print_hashmap(map_t &hashMap)
{
   for (auto it = hashMap.begin(); it != hashMap.end(); it++)
   {
      std::cout << "(";
      for (auto &elem : it->first)
         std::cout << elem << ", ";
      std::cout << "): ";
      for (auto &elem : it->second)
         std::cout << elem << ",";
      std::cout << std::endl;
   }
}

template <typename T>
void print_arr1D(T *array, long dim)
{
   std::cout << "[";
   for (long i = 0; i < dim; i++)
   {
      std::cout << array[i] << ", ";
   }
   std::cout << "]" << std::endl;
}

template <typename T>
void print_vector1D(std::vector<T> vec)
{
   std::cout << "[";
   for (auto &elem : vec)
   {
      std::cout << elem << ", ";
   }
   std::cout << "]" << std::endl;
}

template <typename T>
void print_vector2D(std::vector<std::vector<T>> vec)
{
   std::cout << "[\n";
   for (auto &elem : vec)
   {
      print_vector1D(elem);
   }
   std::cout << "]" << std::endl;
}

template <typename T>
T square(T input)
{
   return input * input;
}

template <typename T>
short sign(T input)
{
   if (input > 0)
      return 1;
   else if (input < 0)
      return -1;
   else
      return 0;
}

template <typename T>
key_type get_grid_vertex(T *observations, int *consideredColumns, int dim, T cellWidth)
{

   auto result = key_type(dim);
   for (int i = 0; i < dim; i++)
   {
      result[i] = (index_t)observations[consideredColumns[i]] / cellWidth;
   }

   return result;
}

/*
 * Adds an observation to all adjacent grid cells
 *
 * This funciton works recursively.
 *
 * Parameters
 * ----------
 * row:
 *    Index of the observation being considered.
 * hashMap:
 *    Set of grid cells and corresponding observations. This is filled here.
 * gridVertex:
 *    Key of the vertex in the grid where the considered observation is located.
 * distancesToCenter:
 *    Distance between the cell's mid point and the observation.
 * reflect:
 *    Whether to use reflecting boundary conditions.
 * dim:
 *    Dimension of the considered data space.
 * index:
 *    Current index under consideration. Is incremented in every recursion level.
 * squareDistance:
 *    Lower bound for the squared distance of the considered point to the considered
 *    neighbouring cells computed based on the dimensions already processed.
 * halfCellWidth:
 *    Half of the width of a cell
 * squareDistanceBound
 *    Square of the maximal considered distance between two data points. I.e.,
 *    square cell width.
 *
 */
template <typename T>
void fill_in_neighbours(index_t row, map_t &hashMap, key_type &gridVertex, std::vector<T> &distancesToCenter,
                        std::vector<bool> &reflect, int dim, int index,
                        T squareDistance, T halfCellWidth, T squareDistanceBound)
{

   // recursion end
   if (index >= dim)
   {
      hashMap[gridVertex].push_back(row);
      return;
   }

   // one option is not to change the current dimension
   fill_in_neighbours<T>(row, hashMap, gridVertex, distancesToCenter, reflect, dim,
                         index + 1, squareDistance, halfCellWidth, squareDistanceBound);

   auto distanceToThisCenter = distancesToCenter[index];
   if (distanceToThisCenter)
   {
      // check if we are still within the admissible radius
      auto direction = sign(distanceToThisCenter);
      auto newSquareDistance = squareDistance + square(direction * halfCellWidth - distanceToThisCenter);

      if ((newSquareDistance <= squareDistanceBound) &&
          (direction > 0 || gridVertex[index] || !reflect[index]))
      {

         // change
         gridVertex[index] += direction;

         // the other option to consider the left or right neighbor
         fill_in_neighbours<T>(row, hashMap, gridVertex, distancesToCenter,
                               reflect, dim, index + 1, newSquareDistance, halfCellWidth, squareDistanceBound);

         // undo the change
         gridVertex[index] -= direction;
      }
   }
}

template <typename T>
void fill_hashmap(map_t &hashMap, T **observations, int *consideredColumns,
                  std::vector<bool> &reflect, int dim, long lenObservations, T guaranteedLookupDistance)
{

   auto cellWidth = guaranteedLookupDistance * 2;

   for (index_t i = 0; i < lenObservations; i++)
   {
      auto gridVertex = get_grid_vertex<T>(observations[i], consideredColumns, dim, cellWidth);

      // The sign of distancesToCenter indicates if the point is closer to the
      // lower or upper end of the cell in a dimension. The value is the
      // distance to the cell center.
      std::vector<T> distancesToCenter = std::vector<T>(dim);
      for (int j = 0; j < dim; j++)
      {
         distancesToCenter[j] = observations[i][consideredColumns[j]] - gridVertex[j] * cellWidth - guaranteedLookupDistance;
      }

      fill_in_neighbours<T>(i, hashMap, gridVertex, distancesToCenter, reflect,
                            dim, 0, 0., guaranteedLookupDistance, guaranteedLookupDistance * guaranteedLookupDistance);
   }
}

const double MIN_log1pexp = -10;
const double RESOLUTION_log1pexp = -1e-3; //-1e-5;
std::vector<double> log1pexp_cache;

void init_log1pexp_cache()
{
   std::size_t cache_size = std::size_t(std::ceil(MIN_log1pexp / RESOLUTION_log1pexp));
   cache_size += 1;
   log1pexp_cache.resize(cache_size);
   for (size_t i = 0; i < cache_size; i++)
   {
      log1pexp_cache[i] = log1p(exp(RESOLUTION_log1pexp * i));
   }
}

template <typename T>
double log1pexp(T x)
{
   if (x <= MIN_log1pexp)
   {
      return exp(x);
   }
   else
   {
      auto a = x / RESOLUTION_log1pexp;
      size_t i = size_t(a);
      a -= i;
      return (1 - a) * log1pexp_cache[i] + a * log1pexp_cache[i + 1];
   }
}

template <typename T>
T compute_log_likelihood_element(T *observation, T *sample, int *consideredColumns,
                                 int *mode, T *inverseBandwidth, T logNormalization, int dim, T halfGuaranteedLookupDistance)
{

   T result = -logNormalization;
   for (int i = 0; i < dim; i++)
   {
      auto j = consideredColumns[i];
      result -= square(observation[j] - sample[j]) / 2;
      if (mode[j] && observation[j] <= halfGuaranteedLookupDistance)
      {
         if (mode[j] == 1)
            result += log1pexp((-2) * observation[j] * sample[j]);
         else
            result += log1pexp((-2) * observation[j] * sample[j] - (observation[j] + sample[j] + 0.5 * inverseBandwidth[j]) * inverseBandwidth[j]);
      }
   }

   return result;
}

template <typename T>
void compute_log_likelihood(map_t &hashMap, T **observations, T **sample, int *consideredColumns,
                            int *mode, T *inverseBandwidth, T logNormalization, int dim, long lenObservations,
                            long lenSample, T guaranteedLookupDistance, T *out)
{

   auto logP = std::vector<std::vector<T>>(lenObservations);

   if (log1pexp_cache.empty())
   {
      init_log1pexp_cache();
   }

   auto logPMax = std::vector<T>(lenObservations, -INFINITY);
   auto cellWidth = guaranteedLookupDistance * 2;
   auto halfGuaranteedLookupDistance = guaranteedLookupDistance / 2;
   T newLogPValue;

   for (index_t i = 0; i < lenSample; i++)
   {
      auto indexSearch = hashMap.find(get_grid_vertex<T>(sample[i], consideredColumns, dim, cellWidth));

      if (indexSearch != hashMap.end())
      {
         auto &thisSample = sample[i];
         for (auto &j : indexSearch->second)
         {
            newLogPValue = compute_log_likelihood_element<T>(observations[j], thisSample,
                                                             consideredColumns, mode, inverseBandwidth, logNormalization, dim, halfGuaranteedLookupDistance);
            logP[j].push_back(newLogPValue);
            if (logPMax[j] < newLogPValue)
               logPMax[j] = newLogPValue;
         }
      }
   }

   T result = 0;
   T resultTmp;
   T logPMaxTmp;
   auto logLenSample = log(lenSample);
   for (index_t i = 0; i < lenObservations; i++)
   {
      logPMaxTmp = logPMax[i];
      resultTmp = 0;
      for (auto &val : logP[i])
      {
         resultTmp += exp(val - logPMaxTmp);
      }
      out[i] = (logPMaxTmp + log(resultTmp) - logLenSample);
   }
}

template <typename T>
void print_arr2D(T **array, long dim1, long dim2)
{
   std::cout << "[" << std::endl;
   for (long i = 0; i < dim1; i++)
   {
      print_arr1D<T>(array[i], dim2);
   }
   std::cout << "]" << std::endl;
}

template <typename T>
map_t *construct_grid(T **observations, int *consideredColumns, int *mode,
                      int dim, long lenObservations, T guaranteedLookupDistance)
{
   std::vector<bool> reflectVector = std::vector<bool>(dim);

   for (int i = 0; i < dim; i++)
   {
      reflectVector[i] = (bool)mode[consideredColumns[i]];
   }

   // create hash map containing the observations
   auto hashMap = new map_t();

   fill_hashmap<T>(*hashMap, observations, consideredColumns, reflectVector,
                   dim, lenObservations, guaranteedLookupDistance);
   return hashMap;
}
