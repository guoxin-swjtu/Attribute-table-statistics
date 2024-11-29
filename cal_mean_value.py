"这串代码是为了根据SHP和TIF计算polygon的平均值"


import geopandas as gpd
import rasterio
import numpy as np
import os
from rasterio.mask import mask

# 读取矢量文件A
shp_file = "/media/xsar/F/guo-x/static/sta/SHP/Numb.48023_V3.shp"
A = gpd.read_file(shp_file)

# 检查和打印CRS
print("CRS of A:", A.crs)

# 读取文件夹B中的所有tif文件
tif_folder = "/media/xsar/F/guo-x/static/sta/data_sta/"
tif_files = [f for f in os.listdir(tif_folder) if f.endswith('.tif')]

# 删除无效的几何对象
A = A[A.is_valid]

# 遍历tif文件并计算每个tif对应的平均值
for tif_file in tif_files:
    tif_path = os.path.join(tif_folder, tif_file)
    
    # 读取栅格文件
    with rasterio.open(tif_path) as src:
        print(f"Processing raster: {tif_file} with CRS: {src.crs}")
        
        # 确保栅格与shp文件有相同的CRS
        if A.crs != src.crs:
            A = A.to_crs(src.crs)
            print("CRS of A has been transformed to match the raster CRS.")

        # 为shp文件添加一列存储该tif的平均值，初始化为NaN
        tif_column_name = tif_file.split('.')[0]  # 使用tif文件名作为列名
        A[tif_column_name] = np.nan

        # 遍历A中的每个polygon
        for idx, row in A.iterrows():
            # 获取当前polygon的几何数据
            geom = [row['geometry']]

            # 使用rasterio的mask函数裁剪tif文件的内容
            out_image, out_transform = mask(src, geom, crop=True)

            # 计算有效像素的平均值
            # out_image为一个三维数组，包含多个波段的数据，我们只处理第一个波段
            out_image = out_image[0]  # 选择第一个波段
            out_image = out_image[out_image != src.nodata]  # 排除nodata值

            if out_image.size > 0:  # 确保有有效像素
                mean_value = out_image.mean()  # 计算平均值
            else:
                mean_value = np.nan  # 如果没有有效像素，则设为NaN

            # 将平均值写入到A的属性表中
            A.at[idx, tif_column_name] = mean_value

# 将更新后的shp文件保存到新文件
output_shp_file = "/media/xsar/F/guo-x/static/sta/SHP/Updated_with_avg_values.shp"
A.to_file(output_shp_file)

print("完成了所有tif文件的平均值计算并更新了shp文件。")



