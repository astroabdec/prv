待更新中...

----





大致内容包括 输入每次观测每个order的光谱数据，对不同观测做shift之后叠加得到template，之后可以得到一个不同观测日期和不同order的RV矩阵，通过vanking的过程得到相对视向速度及误差





将pipeline分成了三个独立的code
文件夹结构：
- prv文件夹中的FEROS文件夹中
  - Notebook文件夹：
    - Get_Absolute_RV是利用iSpec获取绝对视向速度，加入了去除telluric lines，输入是从ESO下载的FEROS光谱中单独的那个fits文件
      - note：
    - Get_orders是从ESO下载的FEROS的光谱数据3081.fits中找到每一个order的光谱并进行处理，得到计算prv过程的输入数据，并存到相应的路径中
      - note：请将下载解压好的FEROS光谱文件夹放在FEROS/Spectra/中，在Get_orders notebook中修改target name就可以
  - Spectra文件夹：
      - 
- prv文件夹中的Get_prv文件夹中
    -
