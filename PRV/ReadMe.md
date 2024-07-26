待更新中...

----





大致内容包括 输入每次观测每个order的光谱数据，对不同观测做shift之后叠加得到template，之后可以得到一个不同观测日期和不同order的RV矩阵，通过vanking的过程得到相对视向速度及误差



文件夹结构：

- 将pipeline分成了三个独立的code
  - prv文件夹中的FEROS文件夹中
    - Notebook文件夹：
      - Get_Absolute_RV是利用iSpec获取绝对视向速度，加入了去除telluric lines
        - note：注意修改iSpec路径为安装路径
      - Get_orders是从ESO下载的FEROS的光谱数据3081.fits中找到每一个order的光谱并进行处理，得到计算prv过程的输入数据，并存到相应的路径中
        - note：请将下载解压好的FEROS光谱文件夹放在FEROS/Spectra/中，之后在Get_Absolute_RV中设置hd_path，在Get_orders的notebook中修改target name就可以
        - 我们在对order处理时只保留了每个order中间的3000个pixel，并且
    - Spectra文件夹：
      - Absolute RV文件夹中HD 81797是袁老师绝对视向速度用的标准星，notebook中temp_path设置成这个
      
        ```no-highlight
        hd_path = '../Spectra/HD 92588/'
        temp_path = '../Spectra/Absolute RV/HD 81797/'``` 
        ```
    
  - prv文件夹中的HRS_prv文件夹中
      
      - Get_prv 是在王雪凇老师提供的code基础上修改的获取高精度相对视向速度的pipeline，其中增加了vanking中去除outlier的部分，还没有增加将结果加入制作template之后迭代的过程，这里的输入文件默认是做好barycentric correction的 (FEROS光谱是做过的) ，对没有做过的数据可以参考王老师提供的 mktpl530.py中第一个函数
      - feros文件夹中会存放 对应Get_orders中target name的输入文件 (切片后的所有order的光谱)，同样只用在Get_prv中修改target_name即可
      - barycorr文件夹是存放 获取BJD的fits文件

