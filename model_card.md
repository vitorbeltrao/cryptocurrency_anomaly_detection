# Model Operation

## Overview

The statistical model used in this project is an anomaly detection algorithm based on statistical methods. The model's goal is to identify data points that deviate significantly from normal behavior, allowing the detection of unusual events or patterns in the data.
***

## Model Operation

The model uses statistical techniques to characterize data distribution and identify values that deviate from expected behavior. It is based on the following steps:

1. Preprocessing: The data goes through preprocessing to ensure data quality and consistency. In this step, the following tasks are performed:

* Outlier Removal: Using the interquartile range method (boxplot), we identify and remove outliers that could affect statistical estimation.

2. Parameter Estimation: Based on preprocessed data, we estimate statistical parameters that describe the data distribution. Some commonly used parameters include mean, standard deviation, quartiles, and other relevant statistical moments.

3. Threshold Calculation: From the estimated data distribution, we set statistical thresholds that define the range of expected behavior. Data points outside these limits are considered anomalies.

4. Anomaly Detection: Data points are compared to the defined thresholds and classified as anomalies or non-anomalies. Identified anomalies are marked for further analysis and investigation.
***

## Model Limitations

It's important to highlight some limitations of the statistical model:

1. Dependence on Statistical Assumptions: The model assumes that the data follows a specific statistical distribution or approximates it. If the data exhibits characteristics that deviate from these assumptions, the model's effectiveness might be reduced.

2. Sensitivity to Outliers: The model can be influenced by outliers or extreme values in the data. Although preprocessing includes outlier removal, it's possible that some outliers won't be detected, or other unusual data might be incorrectly identified as anomalies.

3. Difficulty Adapting to Pattern Changes: The model is more effective when data patterns remain relatively stable over time. If significant changes occur in behavior patterns, the model might struggle to adapt to those changes.
***

## Model Output

The model's output is a boolean value indicating whether a given data point is considered an anomaly or not. The *is_anomaly* function is responsible for performing this verification.

The logic behind determining an anomaly is based on comparisons between the value to be verified and the statistical parameters of the model, including the mean, standard deviation, and established limit.

* If the compared value is above the upper limit (mean + 3 x standard deviation) or below the lower limit (mean - 3 x standard deviation), it's considered an anomaly.

* Otherwise, the value is considered normal.

This approach is based on the assumption that data follows a normal distribution. By applying outlier removal to the data, we aim to bring it closer to a normal distribution, allowing the model to leverage statistical theory associated with that distribution to identify anomalies.

In practice, the model's output is used to quickly identify data points deviating from expected behavior. With this information, it's possible to detect anomalies, atypical behaviors, or out-of-pattern events, providing valuable insights for analysis and decision-making.

In the context of the anomaly detection project, the model's output is logged through messages. When a value is identified as an anomaly, an email message is generated for the responsible party. If the value isn't an anomaly, a log message is recorded stating that the value is considered normal. This information helps system users understand and interpret the model's results.
***

## Example of Results

The following image illustrates an example application of the statistical model. Let's imagine that the two graphs below represent a distribution of our data, respectively, in a histogram and a boxplot.

**Histogram**

![Normal Distribution Histogram](https://github.com/vitorbeltrao/cryptocurrency_anomaly_detection/blob/main/images/distribui%C3%A7%C3%A3o%20normal.png?raw=true)

In a simple way, we can estimate the data distribution probabilities if it's normal (as shown in the graph above). In our model, we will adopt 3 standard deviations as the limit to be tested. Thus, any point that falls to the right or left of this limit will be considered an anomaly. See this illustrated by the boxplot below.

**Box-Plot**

![Boxplot](https://github.com/vitorbeltrao/cryptocurrency_anomaly_detection/blob/main/images/boxplot.png?raw=true)

Notice that all the green points are outside the considered limit and hence, they are considered outliers (anomalies).

In this example, the model accurately identified data points that deviated from expected behavior, providing valuable insights into uncommon events or potential data issues.
***

## Final Considerations

The statistical model used in this project offers an efficient approach to detect anomalies in data, enabling the identification of patterns or unusual events. Preprocessing helps in preparing data for better statistical estimation. However, it's important to consider the mentioned limitations and assess whether the model is suitable for the specific data context and project requirements. Continuous monitoring of the model's performance and adjustments as needed are recommended to ensure accurate and reliable results.