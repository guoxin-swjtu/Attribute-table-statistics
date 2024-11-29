"这串代码是因为部分分辨率低，没办法计算平均值，从而计算其中心点的值，然后填充到空值中"

import geopandas as gpd
import rasterio
import os
import pandas as pd
import numpy as np

# 读取Shapefile
shapefile_path = '/media/xsar/F/guo-x/static/sta/SHP/Updated_with_avg_values.shp'  # 替换为实际的shp文件路径
gdf = gpd.read_file(shapefile_path)

# 输入包含空值的列名
columns_with_na = ['AP', 'MAGT', 'MAAT', 'ET', 'PISR','SCD']  # 替换为实际有空值的列名列表

# 设置栅格文件夹路径
raster_folder = '/media/xsar/F/guo-x/static/sta/data_sta'  # 替换为tif文件所在的文件夹路径

# 总记录数
total_records = len(gdf)

# 初始化列状态字典
column_status = {column: 'Pending' for column in columns_with_na}

# 逐列遍历并批量处理所有polygon的中心点
for column in columns_with_na:
    if column_status[column] == 'Pending':  # 仅当该列尚未完成时处理
        print(f"Processing column: {column}")
        
        # 动态构建tif文件路径，假设tif文件名与列名相同
        raster_path = os.path.join(raster_folder, f'{column}.tif')
        
        # 检查tif文件是否存在
        if not os.path.exists(raster_path):
            print(f"Warning: TIF file {raster_path} not found.")
            continue
        
        # 打开栅格文件
        with rasterio.open(raster_path) as raster:
            transform = raster.transform
            
            # 获取所有polygon的中心点坐标
            centroids = gdf.geometry.centroid
            coords = [(centroid.x, centroid.y) for centroid in centroids]
            
            # 使用rasterio.sample批量提取栅格值
            samples = list(raster.sample(coords))  # 批量读取多个点的值
            
            
            # 将获取的样本值更新到Shapefile中
            for idx, sample in enumerate(samples):
                # 填充Shapefile的空值列
                if sample is None:
                # print(f"Warning: No value found for centroid {coords[idx]} in raster for {column}. Skipping.")
                    continue  # 跳过此点，不填充值
                if pd.isna(gdf.at[idx, column]):  # 如果该列为空
                    gdf.at[idx, column] = sample[0]  # sample[0]是该位置的像素值

        # 更新该列的状态为已完成
        column_status[column] = 'Completed'
        print(f"Column {column} processing complete.")

    # 打印列的处理状态
    print(f"Column statuses: {column_status}")

# 保存更新后的Shapefile
gdf.to_file('/media/xsar/F/guo-x/static/sta/SHP/Updated.shp')

# 完成处理后，输出最终消息
print("Processing complete. Updated Shapefile has been saved.")
