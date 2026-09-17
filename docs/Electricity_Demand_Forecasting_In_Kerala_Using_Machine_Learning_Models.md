**_2023 3rd International Conference on Intelligent Technologies (CONIT) Karnataka, India. June 23-25, 2023_** 

# Electricity Demand Forecasting In Kerala Using Machine Learning Models 

Anna Saji Arya Prakash M Soumya Krishnan _Department of Computer Science & IT Department of Computer Science & IT Department of Computer Science & IT, School of Computing, Amrita Vishwa School of Computing, Amrita Vishwa School of Computing, Amrita Vishwa Vidyapeetham Vidyapeetham Vidyapeetham,_ Kochi Campus, India Kochi Campus, India Kochi Campus, India. annasaji2000@gmail.com aryaprakash713@gmail.com soumyamahesh15@gmail.com 

**_<mark>Abstract</mark>_ - In the contemporary era, energy has evolved into a necessity for day-to-day life. Forecasting the demand for electricity is an extremely challenging undertaking.** **<mark>Forecasting the electricity accurately helps to run the power systems efficiently and effectively.</mark>** 

**<mark>In this work, we have developed an electricity demand forecasting model that predicts electricity demand using our own dataset. Our dataset contains 10 years of data (January 2013 to December 2022).The electricity demand data was taken from the Kerala State Electricity Board (KSEB). Linear Regression (LR), Decision Tree (DT), Random Forest (RF), Support Vector Regression (SVR), K-Nearest Neighbors (KNN), XGBoost, Artificial Neural Network (ANN) based on Machine Learning (ML) methods have been applied to observe how these algorithms perform in forecasting electricity. The performance of the discussed ML methods has been analysed based on various evaluation metrics such as accuracy, MAE, MSE, and RMSE. The outcomes obtained from the analysis show that the Random Forest ML approach outperforms the other conventional ML approaches in terms of accuracy, MAE, MSE, and RMSE since it has the highest accuracy (82.72%) and the lowest MAE, MSE, and RMSE score (0.038, 0.002, and 0.054, respectively) compared to the other discussed conventional ML approaches.</mark>** 

**_<mark>Keywords-Electricity Demand Forecast, Machine Learning; Prediction, Linear Regression (LR), Decision Tree (DT), Random Forest (RF), Support Vector Regression (SVR), K Nearest Neighbors (KNN), XGBoost, Artificial Neural Network (ANN).</mark>_** 

## <mark>I. INTRODUCTION</mark> 

<mark>Every nation's economic development is directly correlated with its power infrastructure, network, and availability because electricity has become such a crucial component of daily living in the modern world. The need for electricity for domestic and commercial use has consequently expanded globally. In contrast, fluctuating electricity rates throughout time have concealed the fact that global demand for electricity exceeds supply. In order to prepare ahead and urge consumers to conserve energy, power generators, distributors, and suppliers have conducted a number of studies to forecast future electrical energy demand for business and residential applications.</mark> 

<mark>Even though there has been a lot of recent study on the topic of forecasting power demand, more reliable and precise electricity demand forecast models are still required. An accurate forecast of the variance in future power demand is essential for both electric consumers and utilities since it is employed in decision-making. However, the main challenges in predicting future electricity demand are the multiple</mark> 

<mark>contributing factors, such as varying climate, humidity, temperature, calendar indications, occupancy patterns, and society standards. In such a dynamic environment, conventional forecasting techniques are insufficient, necessitating the use of more sophisticated methodology. With the aid of machine learning, we'll suggest a system that can forecast future electricity demand.</mark> 

## <mark>II. RELATED WORKS</mark> 

<mark>Camurdan et al. [1], developed a method to predict electricity demand using three different machine learning models. They use different evaluation matrices to test the accuracy of the results. Here the highest accuracy of 98% was obtained from the random forest model.</mark> 

<mark>Anik et al .[2],  a simultaneous equation framework was applied to an annual database over a 47-year period (19722018) to forecast future energy demand.</mark> 

<mark>Shabbir et al. [3], applied three different ML algorithms: LR, tree based regression, and SVM-based regression on a large dataset of an Estonian household. The results show that SVM is the most effective method since it provides the lowest Root Mean Square Error(RMSE).</mark> 

<mark>Liu et al. [4],</mark> ANN , SVM and hybrid machine learning approaches were compared by Liu et al. They found that each approach had its own advantages and disadvantages, as well as distinct features and applications in various contexts. 

<mark>Gajowniczek et al. [5], c</mark> reated an algorithmic method for load modelling through peak detection. SVM and ANN both produce findings for peak classification that are very promising. 

<mark>Jain et al. [6],</mark> put forward a method for forecasting power demand using the ARIMA model. The quarterly ARIMA model was found to be the most accurate model for forecasting energy consumption in IIT for the years 2004– 2008.(ISM). This paper's drawback is that the ARIMA model may have trouble predicting high values. 

<mark>Mati et al. [7], proposed a multiple regression time series modelling approach to predict Nigeria’s energy demand using previous data of 1970 to 2005. One drawback of the time series models is that they cannot clearly represent technologies and rely on heavily aggregated data, as well as ignoring the technically most efficient solutions, resulting in an underestimation of energy improvement potential.</mark> 

<mark>Behm et al. [8], presented a method for forecasting longterm climate hourly power consumption using ann. Their main contribution is to present a new method to forecast electricity loads as necessary input data for energy system</mark> 

**979-8-3503-3860-7/23/$31.00 ©2023 IEEE** 

1 

Authorized licensed use limited to: Indian Institute of Information Technology Kottayam. Downloaded on September 17,2026 at 04:42:39 UTC from IEEE Xplore.  Restrictions apply. 

<mark>modelling. The limitation is that they didn’t use the correct scaling method for loads.</mark> 

<mark>Islam et al. [9], d</mark> emonstrated a load prediction method based on LSTM in Chattogram, Bangladesh. The results show that the SVM performs better. One of the major drawbacks of the LSTM is that crucial variables like the batch size, neuron size, number of time steps and others must be manually selected and rely on the researcher's level of experience. 

<mark>Eseye et al. [10], t</mark> he use of a ml-based hybrid selection of features approach to retrieve the most relevant and nonredundant data for improved short-term forecasting of power consumption in distributed power systems. 

<mark>Usha et al. [11], introduced to numerous prognosis and</mark> predicting techniques that were developed in the field of electricit <mark>y. This project’s main goal is to use a seasonal data method to anticipate power consumption. The limitations of this paper is that different consumers use different meters, either standard or smart meters, and their electricity usage varies depending on the meter.</mark> 

<mark>Deng et al. [12], f</mark> or forecasting Singapore's short-term power usage, a time series analysis was recommended. The seasonal ARIMA model and the multiplicative decomposition model are discussed as time series models. The difficulty in fitting a trend line is one of the study's shortcomings since load demands typically change greatly with regard to seasons and temperatures. 

<mark>Patel et al. [13], introduced a time series model for predicting the future load demand. With the aid of a projected power system or future consumption, an electric utility or energy management system may plan effectively. The paper’s drawbacks include that consumption may fluctuate as a result of price changes, making it difficult to obtain reliable data for predicting.</mark> 

<mark>Rabbi et al. [14], p</mark> resented a multivariate time series model to predict Bangladesh's yearly demand of electricity. In order to predict Bangladesh's electricity requirements, a time series with multiple variables is used because it provides more information. 

<mark>In [15], T</mark> he authors made an estimate of the Philippines' energy usage.. This study aims to predict how much electricity will be used for domestic, business, and institutional purposes in the Philippines. In this study, a sort of time series analysis model called the ARIMA approach was used. 

## <mark>III. PROPOSED METHODOLOGY</mark> 

<mark>There are a total of three types of data in the dataset, including energy, weather, and population density. The three procedures of cleaning, normalising, and organising data are collectively referred to as data pre-processing are applied on the dataset. The final dataset is obtained after the preprocessing phase and is then used for further implementation.</mark> The final dataset consists of two parts: the training set and the testing set. <mark>The training sets are subjected to machine learning techniques. The prediction models are created, and after making predictions on the test set, they calculate their percentage accuracy and compare their results.</mark> 

## <mark>The different machine learning models used are:</mark> 



<mark>Fig. 1. Methodology</mark> 

## _<mark>A. Linear Regression</mark>_ 

Regression is performed using the linear regression algorithm, a supervised machine learning method. It merely checks to see if the input and output variables are linearly related. Because it presupposes a linear relationship between a dependant variable (y) and an independent variable, linear regression is the most used modelling technique (x). 

## _<mark>B. Decision Tree</mark>_ 

In contrast to other supervised learning techniques, the decision tree strategy can handle both classification and regression. Using a Decision Tree, a training model is created that can be used to forecast the class or value of the target variable by learning fundamental choice rules produced from previous data. 

## _<mark>C. Random Forest</mark>_ 

Using data samples as a starting point, the random forest technique builds decision trees, gets predictions from each one, and uses voting to choose the best course of action. It is an ensemble method that is better to a single decision tree because it averages the results to minimise over fitting. 

## _<mark>D. Support Vector Machine</mark>_ 

<mark>It is a type of regression algorithm. It keeps all essential traits, defining the algorithm with the widest margin. Given all the possible possibilities, it is difficult to predict the information as a result. Tolerance or epsilon are used in regression to approximate the SVM that was asked to solve the issue. The primary goals are to eliminate error and personalise the hyper plane.</mark> 

## _<mark>E. K-Nearest Neighbors</mark>_ 

It addresses issues with categorization and regression. <mark>That is easy to comprehend and put into practice. Its primary drawback is that it becomes slower as data sizes grow.</mark> When performing classification or regression, KNN chooses the label with the highest frequency or averages the labels after calculating the distances between a query and all the samples in the data that are most similar to it. 

## _<mark>F. ANN</mark>_ 

ANN is composed of several interconnected neurons that mimic the way the brain works. These neurons have the capacity to learn, generalise training data, and draw inferences from complicated data. These networks are used to solve optimisation problems, identify patterns and trends, and perform classification and prediction tasks. With only the training data, ANN learns without any programming (known input and target output). 

2 Authorized licensed use limited to: Indian Institute of Information Technology Kottayam. Downloaded on September 17,2026 at 04:42:39 UTC from IEEE Xplore.  Restrictions apply. 

## _<mark>G. XGBoost</mark>_ 

It is a collective learning method that combines the output from a number of tiny, ineffectual models to create a bigger, more precise prediction. Due to its ability to manage enormous datasets and beat other algorithms in a variety of machine learning tasks. One of the key characteristics of XGBoost is how effectively it handles missing values. As a result, it can deal with real-world data that contains missing values without the need for extensive pre-processing. 

## _<mark>H. Dataset</mark>_ 

<mark>To create the dataset for Kerala, data was gathered from several sources. The dataset includes data for the years 0101-2013 to 31-12-2022, or more than ten years. The following features have been taken into consideration as the primary features for our study: Date, Demand (MW), Temperature, Dew Point, Humidity, Pressure, Wind speed, and Population Density. We discovered that these characteristics have a strong correlation with electricity demand after studying some research papers and articles.</mark> 

<mark>1. The data for demand (mw) was obtained from Kerala State Electricity Board (KSEB).</mark> 

<mark>2. The weather information (temperature, dew point, humidity, pressure, and wind speed) was collected from the TckTckTck.org website.</mark> 

<mark>3. The population density data was collected from the worldpopulationreview.com website</mark> 

- <mark>IV. EXPERIMENT AND RESULT ANALYSIS</mark> 

## _A. Evaluation of Performance_ 

The results from the models are determined along with conventional evaluation measures like MAE, MSE, and RMSE. Based on the obtained results, the optimal model is chosen. 

<mark>TABLE I. ANALYSING THE LINEAR REGRESSION MODEL AND ITS OUTCOMES</mark> 



<!-- Start of picture text -->
Prediction Enrors and accuracy score ofLR.<br><!-- End of picture text -->



<!-- Start of picture text -->
s Predictions made by Linear Regression model<br>S5 0719s Spe)<br>Zos- i {— Predicted<br>£ Si , ; i<br>Sos- H i nN iy<br>Bos i b udi WeyTTBita il !<br>2 i ig iiy if<br>S won i What<br>g o4- | | nd | Shy erat<br>a3 03- | {oer i } i<br>33 02- ¥ H |tale | Citai| athim)<br>git ded Ags ois tat! lt<br>z i ’ ) ’ ’ ) ) ’<br>2900 3000 3100 3200 3300 400 3500 3600<br>Time<br><!-- End of picture text -->

<mark>Fig. 2. Graphical Representation of Actual Vs. Predicted Results for Linear Regression</mark> 



<!-- Start of picture text -->
Linear Regression model<br>07 oe ms<br>06 ° % : e<br>05 - — ><br>3°<br>2<br>. 04. ’ >.<br>a<br>03- crete<br>02- for° °<br>1 °<br>ol 02 03 of 05 06 7<br>Predicted<br><!-- End of picture text -->

<mark>Fig. 3. Actual Vs. Predicted Observations for Linear Regression</mark> 

<mark>TABLE II. ANALYSING THE DECISION TREE MODEL AND ITS OUTCOMES</mark> 



<!-- Start of picture text -->
ee<br>aes a<br><!-- End of picture text -->



<!-- Start of picture text -->
Predictions made by Decision Tree model<br>=23 07o6- tae ., bd i —-@- ActualPredicted<br>z<br>3> 0s- U q | | UP Be<br>ctS 04 \« rifteatf i 01 tat<br>3 : 1 i<br>g 03- x \ ied ) '<br>3° LS aaaj "ae RC{ iN tolESRI| ho<br>S 01- o<br>2900 3000 3100 3200 Time3300 400 3500 3600<br><!-- End of picture text -->

<mark>Fig. 4. Graphical Representation of Actual Vs. Predicted Results for Decision Tree</mark> 



<!-- Start of picture text -->
Decision Tree model<br>07- . ar<br>°cp. % 2%<br>06 - 5 Wey ed<br>°& 5! et<br>Os - con ‘We OP<br>=3 . ce ove °<br>a oa. ° °<br>2 e ones rar<br>2 ee os<br>03- 4 Gg Oe<br>Py e<br>><br>°° 2 a<br>e<br>o1 02 03 04 os 06 07<br>Predicted<br><!-- End of picture text -->

<mark>Fig. 5. Actual Vs. Predicted Observations for Decision Tree</mark> 

3 Authorized licensed use limited to: Indian Institute of Information Technology Kottayam. Downloaded on September 17,2026 at 04:42:39 UTC from IEEE Xplore.  Restrictions apply. 

<mark>TABLE III. ANALYSING THE RANDOM FOREST MODEL AND ITS OUTCOMES</mark> 



<!-- Start of picture text -->
=n ror<br>[Mewsemvee ee<br><!-- End of picture text -->



<!-- Start of picture text -->
E o7- made by Random Forest~e- modelActual<br>= as Predicted<br>Eos Y bl i<br>>25 os Theale} 1 aio: iy1 [3<br>8 os. Pig teat<br>‘o 03- vet{ it ‘ “4<br>33 || il Gap | be<br>So2- FF iy3 tt eR h % ane 5<br>> | rT} bal 1 14, Ve<br>E wa . a? o) Sq<br>2900 «©3000 «3100 «93200 «3300 42400 §=63500 §=3600<br>Time<br><!-- End of picture text -->

<mark>Fig. 6. Graphical Representation of Actual Vs. Predicted Results for Random Forest</mark> 



<!-- Start of picture text -->
Random Forest model<br>07- hp<br>oe Ve<br>06 - o ® +Oog3-<br>- os<br>= 0s e e 3°<br>3 os ° ° 4e ‘e?.ue<br>02- O<br>ol 02 03 «04 05 06 7<br>Predicted<br><!-- End of picture text -->

<mark>Fig. 7. Actual Vs. Predicted Observations for Random Forest</mark> 

<mark>TABLE IV. ANALYSING THE SUPPORT VECTOR REGRESSION MODEL AND ITS OUTCOMES</mark> 



<!-- Start of picture text -->
Prediction Errors and accuracy score of SVR<br><!-- End of picture text -->



<!-- Start of picture text -->
Predictions made by SVR model<br>Zo7 e- Actual<br>:= o6- HT | teryi<br>oaoo 05- iEeejt v if i HY fs. ~ B)<br>3° Ra Kili: Pag:<br>ae<br>Tw 03- | i ia<br>£0. an hg. Be eta<br>guA Nt omensSok oR,ener ‘4 ffae i Sai i &<br>2900 3000 3100 3200 3300 3400 3500 3600<br>Time<br><!-- End of picture text -->

<mark>Fig. 8. Graphical Representation of Actual Vs. Predicted Results        for SVR</mark> 



<!-- Start of picture text -->
SVR model<br>0<br>07 . Pig Pa<br>06 ~ ie<br>os- e<br>= ° qo<br>o e e<br>B 04- 4 .<br>z e<br>03 td e e<br>ont<br>02- &<br>°<br>o1-<br>ol 02 03 04 05 06 07<br>Predicted<br><!-- End of picture text -->

<mark>Fig. 9. Actual Vs. Predicted Observations for SVR</mark> 

<mark>TABLE V. ANALYSING THE KNN MODEL AND ITS OUTCOMES</mark> 



<!-- Start of picture text -->
or<br><!-- End of picture text -->



<!-- Start of picture text -->
Predictions made by KNN model<br>= 07- e+ Actual ’<br>= — Predicted f “eb<br>Bos. cbt {<br>£ L ih )<br>2. as iff al 1) a {3<br>S03. { \ 1<br>Time<br><!-- End of picture text -->

<mark>Fig. 10. Graphical Representation of Actual Vs. Predicted     Results for KNN</mark> 

4 Authorized licensed use limited to: Indian Institute of Information Technology Kottayam. Downloaded on September 17,2026 at 04:42:39 UTC from IEEE Xplore.  Restrictions apply. 



<!-- Start of picture text -->
KNN model<br>07- © S74.<br>e ef 8<br>°<br>- °<br>os =NE Fi-<br>3 we o2 °<br>e<br>o2- © eS<br>1S a st | | ° | | }<br>ol 02 03 Predicted04 os 06 07<br><!-- End of picture text -->

<mark>Fig. 11. Actual Vs. Predicted Observations for KNN</mark> 

<mark>TABLE VI. ANALYSING THE XG BOOST MODEL AND ITS OUTCOMES</mark> 





<!-- Start of picture text -->
Predictions made by XGBoost model<br>2 o7- ~@- Actual<br>= — Predicted<br>2 ri<br>i nl<br>Boe Y bi | J i i<br> os- f 1 49] | ! El<br>> ‘ ’ iW yy’ | jee<br>=3 o4- |aa‘ Ay | uy1 fily<br>4g ed | I | ' |<br>@ 03- i \ ue<br>3 : il ji! nt | Wo<br>& o2- f pet er ttyl UES<br>g ig es<br>a] 01 “a i | e jOCTjoa seerj i J<br>2900 3000 3100 3200 3300 3400 3500 3600<br>Time<br><!-- End of picture text -->

<mark>TABLE VII. ANALYSING THE ANN MODEL AND ITS OUTCOMES</mark> 



<!-- Start of picture text -->
a<br><!-- End of picture text -->



<!-- Start of picture text -->
Predictions made by ANN<br>=zz5065 a HP Toe ale [dlRayisA ce|<br>05 ap 1 t Hae e ¢<br>3 iF Ht Pl rie fh 1 | A<br>2 ' I}! | fe Ik ty bine<br>2 04 yt ‘ Hy! Met AaM g<br>@ 03 4 4 -<br>; 1BiggI itd, igby | late<br>=z ' 1 1 1 1 1 ' 1<br>Time<br><!-- End of picture text -->

<mark>Fig. 14. Graphical Representation of Actual Vs. Predicted Results for ANN</mark> 



<!-- Start of picture text -->
Fig. 12. Graphical Representation of Actual Vs. Predicted Results 01- i<br>XGBoost<br>01 02 03 04 05 06 07<br>XG Boost model fredices<br><!-- End of picture text -->

<mark>Fig. 15. Actual Vs. Predicted Observations for ANN</mark> 

_<mark>B. Comparison among Various Algorithms</mark>_ 

<mark>The analysis' results show that the Random Forest ML approach performs better than other conventional ML approaches in terms of accuracy, MAE, MSE, and RMSE error rates because it has the highest accuracy (82.55%) and the lowest MAE, MSE, and RMSE error rates (0.0390, 0.0030, and 0.0550 , respectively) when compared to other conventional ML approaches that have been discussed.</mark> 

<mark>The result shown in the table below illustrates the accuracy and error values that were obtained by the used algorithms.</mark> 

<mark>Fig. 13. Actual Vs. Predicted Observations for XG Boost</mark> 

5 Authorized licensed use limited to: Indian Institute of Information Technology Kottayam. Downloaded on September 17,2026 at 04:42:39 UTC from IEEE Xplore.  Restrictions apply. 

### <mark>TABLE VIII.</mark> 

|**algorithms**|**accuracy**|**mae**|**mse**|**rmse**|**algorithms**|
|---|---|---|---|---|---|
|Linear|79.39|0.045|0.003|0.060|Linear|
|Regression|||||Regression|
|Decision<br>Tree|70.74|0.049|0.005|0.073|Decision<br>Tree|
|Random<br>Forest|82.72|0.038|0.002|0.054|Random<br>Forest|
|Support|79.37|0.048|0.003|0.061|Support|
|Vector|||||Vector|
|Regression|||||Regression|
|K Nearest|79.72|0.043|0.003|0.062|K Nearest|
|Neighbors|||||Neighbors|
|XG Boost|82.11|0.038|0.002|0.054|XG Boost|
|ANN|80.31|0.043|0.003|0.058|ANN|





<!-- Start of picture text -->
Accuracy<br>og_ Mim Accuracy<br>o7-<br>os-<br>y 05><br>EY<br>gs 04 -<br>03-<br>02-<br>oa-<br>Ss e € ot os oo ps<br>4"<br>Model<br><!-- End of picture text -->

<mark>Fig. 16. Accuracy</mark> 



<!-- Start of picture text -->
Performance Metrics<br>- mm MSE<br>007 mmm MAE<br>0.06- mm RMSE<br>0.05-<br>5<br>Bo04-<br>&ig 003-<br>0.02-<br>0.01-<br>o.oo- Mims ; = 9 im ' 7<br>a ee aS<br>4<br>MODEL<br><!-- End of picture text -->

<mark>Fig. 17. Error Comparison of the Models</mark> 

## <mark>V. CONCLUSION</mark> 

<mark>A dataset of historical demand data for Kerala, India, covering more than 10 years (January 2013 to December 2023), was successfully created for our thesis. Data was retrieved from the Kerala State Electricity Board (KSEB).</mark> 

<mark>Other important features were manually gathered from various websites as well. Using testing data sets and precise error computation, we assessed the system's dependability and found that the Random Forest Regression Model outperformed rival models.</mark> 

The Random forest ML method has the highest accuracy (82.72%) and the lowest MAE, MSE, and RMSE error rates (0.038, 0.002, and 0.054, respectively) compared to other conventional ML techniques that have been described. Overall findings show that this ML approach surpasses the conventional ML approaches in terms of accuracy, MAE, MSE, and RMSE error rates. 

## <mark>REFERENCES</mark> 

- <mark>[1] Camurdan, Zeynep, and Murat Can Ganiz. "Machine learning based electricity demand forecasting." 2017 International Conference on Computer Science and Engineering (UBMK). IEEE, 2017.</mark> 

- <mark>[2] Anik, Asif Reza, and Sanzidur Rahman. "Commercial energy demand forecasting in Bangladesh." Energies 14.19 (2021): 6394.</mark> 

- <mark>[3] Shabbir, Noman, et al. "Comparison of machine learning based methods for residential load forecasting." 2019 Electric power quality and supply reliability conference (PQ) & 2019 symposium on electrical engineering and mechatronics (SEEM). IEEE, 2019.</mark> 

- <mark>[4] Liu, Zhijian, et al. "Accuracy analyses and model comparison of machine learning adopted in building energy consumption prediction." Energy Exploration & Exploitation 37.4 (2019): 14261451.</mark> 

- <mark>[5] Gajowniczek, Krzysztof, and Tomasz Ząbkowski. "Two-stage electricity demand modeling using machine learning algorithms." Energies 10.10 (2017): 1547.</mark> 

- <mark>[6] P. K. Jain, W. Quamer and R. Pamula, ‘Electricity consumption forecasting using time series analysis,’ in International Conference on Advances in Computing and Data Sciences, Springer, 2018.</mark> 

- <mark>[7] Mati, B. Gajoga, B. Jimoh, A. Adegobye and D. Dajab, ‘Electricitydemand forecasting in nigeria using time series model,’ The Pacific Journal of Science and Technology, 2009.</mark> 

- <mark>[8] Behm, L. Nolting and A. Praktiknjo, ‘Forecasting long-term electricity demand time series using artificial neural networks,’ 2020.</mark> 

- <mark>[9] M. R. Islam, A. Al Mamun, M. Sohel, M. L. Hossain and M. M. Uddin,‘Lstm-based electrical load forecasting for chattogram city of bangladesh,’in 2020 International Conference on Emerging Smart Computing and Informatics (ESCI), IEEE, 2020.</mark> 

- <mark>[10] Eseye, Abinet Tesfaye, et al. "Machine learning based integrated feature selection approach for improved electricity demand forecasting in decentralized energy systems." IEEE Access 7 (2019): 91463-91475.</mark> 

- <mark>[11] T. Usha and S. A. A. Balamurugan, ‘Seasonal based electricity demand forecasting using time series analysis,’ Circuits and Systems, 2016.</mark> 

- <mark>[12] J. Deng and P. Jirutitijaroen, ‘Short-term load forecasting using time series analysis: A case study for singapore,’ in 2010 IEEE Conference on Cybernetics and Intelligent Systems, IEEE, 2010.</mark> 

- <mark>[13] Patel, N., M. Patel, and R. B. Patel. "Electrical Energy Demand Forecasting Using Time Series Approach." International Journal of Technology and Globalisation 29.3s (2020): 594-604.</mark> 

- <mark>[14] Rabbi, Fazly, et al. "A Multivariate Time Series Approach for Forecasting of Electricity Demand in Bangladesh Using ARIMAX Model." 2020 2nd International Conference on Sustainable Technologies for Industry 4.0 (STI). IEEE, 2020.</mark> 

- <mark>[15] Delima, Allemar Jhone P. "Application of Time Series Analysis in Projecting Philippines’ Electric Consumption." International Journal of Machine Learning and Computing 9.5 (2019):694-699.</mark> 

6 Authorized licensed use limited to: Indian Institute of Information Technology Kottayam. Downloaded on September 17,2026 at 04:42:39 UTC from IEEE Xplore.  Restrictions apply. 

