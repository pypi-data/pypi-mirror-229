from sklearn import svm
from sklearn.svm import SVC
from sklearn.metrics import mean_absolute_percentage_error
import mlflow

# Create nested runs
experiment_id = mlflow.create_experiment("experiment1")
with mlflow.start_run(
    run_name="PARENT_RUN",
    experiment_id=experiment_id,
    tags={"version": "v1", "priority": "P1"},
    description="parent",
) as parent_run:
    mlflow.log_param("parent", "yes")
    with mlflow.start_run(
        run_name="CHILD_RUN",
        experiment_id=experiment_id,
        description="child",
        nested=True,
    ) as child_run:
        mlflow.log_param("child", "yes")

print("parent run:")

print("run_id: {}".format(parent_run.info.run_id))
print("description: {}".format(parent_run.data.tags.get("mlflow.note.content")))
print("version tag value: {}".format(parent_run.data.tags.get("version")))
print("priority tag value: {}".format(parent_run.data.tags.get("priority")))
print("--")

# Search all child runs with a parent id
query = "tags.mlflow.parentRunId = '{}'".format(parent_run.info.run_id)
results = mlflow.search_runs(experiment_ids=[experiment_id], filter_string=query)
print("child runs:")
print(results[["run_id", "params.child", "tags.mlflow.runName"]])




model_SVR = svm.SVR()
model_SVR.fit(X_train,Y_train)
Y_pred = model_SVR.predict(X_valid)

print(mean_absolute_percentage_error(Y_valid, Y_pred))

from sklearn.ensemble import RandomForestRegressor

model_RFR = RandomForestRegressor(n_estimators=10)
model_RFR.fit(X_train, Y_train)
Y_pred = model_RFR.predict(X_valid)

mean_absolute_percentage_error(Y_valid, Y_pred)

from sklearn.linear_model import LinearRegression

model_LR = LinearRegression()
model_LR.fit(X_train, Y_train)
Y_pred = model_LR.predict(X_valid)

print(mean_absolute_percentage_error(Y_valid, Y_pred))


# This code is contributed by @amartajisce
from catboost import CatBoostRegressor
cb_model = CatBoostRegressor()
cb_model.fit(X_train, y_train)
preds = cb_model.predict(X_valid)

cb_r2_score=r2_score(Y_valid, preds)
cb_r2_score


