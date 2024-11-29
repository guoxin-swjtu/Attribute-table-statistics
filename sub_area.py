import geopandas as gpd
import numpy as np

# 读取矢量文件A和B
A = gpd.read_file('/media/xsar/F/guo-x/static/sta/SHP/boundary_mountain_regions_hma_v3_4326.shp')
B = gpd.read_file('/media/xsar/F/guo-x/static/sta/SHP/Updated.shp')

# 确保两个文件使用相同的坐标系（CRS）
if A.crs != B.crs:
    B = B.to_crs(A.crs)

# 创建一个新的列Primary_ID_1，并初始化为nan
B['Primary_ID'] = np.nan

# 遍历B中的每个矢量，检查其中心点是否位于A中的任何矢量内
for idx, b_row in B.iterrows():
    # 获取B中当前矢量的几何中心
    b_center = b_row.geometry.centroid
    
    # 遍历A中的每个矢量，检查中心点是否在A的某个矢量内部
    for a_idx, a_row in A.iterrows():
        # 检查B中的中心点是否在A的当前矢量内部
        if a_row.geometry.contains(b_center):
            # 如果是，将A中的Primary_ID值复制到B中的Primary_ID_1列
            B.at[idx, 'Primary_ID'] = a_row['Primary_ID']
            break  # 如果已经找到匹配的矢量，可以跳出内层循环

# 将结果保存到新的Shapefile文件中
B.to_file('/media/xsar/F/guo-x/static/sta/SHP/Numb.48023_sta_last.shp')
