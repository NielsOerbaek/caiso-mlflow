from sklearn.neighbors import KNeighborsRegressor
import sys
import mlflow.tracking
import mlflow.pyfunc
import sklearn.metrics as skm

import prepros

dataset_time = None
mlflow.log_param("dataset_time", dataset_time)

train_x, train_y, test_x, test_y = prepros.get_train_test(dataset_time)

class CAISO(mlflow.pyfunc.PythonModel):
    # California ISO Model (CAISO): It predicts for the next
    # day by taking hourly averages of the three days with highest
    # average consumption value among a pool of ten previous days,
    # excluding weekends, holidays, and past DR event days

    def __init__(self):
        from sklearn.pipeline import Pipeline
        import custom_transformers as ct 
        self.pipeline = Pipeline([
            ("DateParser", ct.DateParser()),
            ("WeekendAdder", ct.WeekendAdder()),
            ("HourAdder", ct.HourAdder()),
            ("DropTime", ct.DropTime()),
        ])

    def fit(self,x,y):
        x = self.pipeline.fit_transform(x)
        # Limit to workdays
        dem = y.loc[x["business_day"] == 1].values
        # Reshape to day/hour matrix
        dem = dem[len(dem)%24:].reshape((len(dem)//24, 24))
        # Only last ten days
        dem = dem[-10:,]
        # Get index of three days with max average consumption
        max_avg = dem.mean(axis=1).argsort()[-3:]
        # Get the hourly for each of these hours
        hour_avg = dem[max_avg,:].mean(axis=0)
        
        self.avg = hour_avg
        return self

    def predict(self, context, samples):
        samples = self.pipeline.transform(samples)
        preds = self.avg[samples["hour"].values]
        return preds

model = CAISO().fit(train_x,train_y)
preds = model.predict(None, test_x)

MAE = skm.mean_absolute_error(test_y, preds)
mlflow.log_metric("MAE", MAE)
print("MAE", MAE)

r2 = skm.r2_score(test_y, preds)
mlflow.log_metric("r2", r2)
print("r2", r2)

print("Saving model")

mlflow.pyfunc.save_model("model", python_model=model, conda_env="conda.yaml")

