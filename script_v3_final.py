import pandas as pd
import numpy as np

train = pd.read_csv("train.csv")
test = pd.read_csv("Test.csv")

#train1 = pd.read_csv("train_5.csv", usecols=["AQB", "FEB15_Bal"])
#test1 = pd.read_csv("test_5.csv", usecols=["AQB", "FEB15_Bal"])

#train = pd.concat((train, train1), axis=1)
#test = pd.concat((test, test1), axis=1)

# del train['Net_relationship_value']
# del test['Net_relationship_value']

# del train['Net_relationship_value_bin']
# del test['Net_relationship_value_bin']

# del train['Branch_City']
# del test['Branch_City']

# #train['Branch_City'] = list(pd.factorize(train['Branch_City']))

# del train['AQB']
# del test['AQB']

# del train['Base_tag']
# del test['Base_tag']

# del train['Total_Invest_in_MF']
# del test['Total_Invest_in_MF']

# del train['salary_dec14']
# del test['salary_dec14']

#print train['salary_Dec14'].head()

#exit()
#train['mva'] = np.median(train['salary_feb15'] + train['salary_jan15'])# + train['salary_dec14'])
#test['mva'] = np.median(test['salary_feb15'] + test['salary_jan15'])# + test['salary_dec14'])

# dict_event = {'N' : 0, 'Y' : 1}
# train['event'].replace(dict_event, inplace = True)
# test['event'].replace(dict_event, inplace = True)

# train['cc_cash_withdrawal_tag'].replace(dict_event, inplace = True)
# test['cc_cash_withdrawal_tag'].replace(dict_event, inplace = True)

# train['Event_and_Credit_Card_cash_withd'].replace(dict_event, inplace = True)
# test['Event_and_Credit_Card_cash_withd'].replace(dict_event, inplace = True)

# train['COC_DAE_EASY_EMI_tag'].replace(dict_event, inplace = True)
# test['COC_DAE_EASY_EMI_tag'].replace(dict_event, inplace = True)

# train = train[['ID', 'pl_holding', 'RESPONDER']]
# test = test[['ID', 'pl_holding', 'RESPONDER']]

# PAPQ - others  or PA
# IF debit spends < 932 1 else 0
# AQB and Net releance - Standard deviation


train = pd.get_dummies(train)
test = pd.get_dummies(test)

test = test[train.columns]

ids_train = train['id']
ids_test = test['id']

y = train['Success']
target_final = test['Success']

train.drop(['id', 'Success'], inplace = True, axis = 1)
test.drop(['id', 'Success'], inplace=True, axis=1)

# SMOTEing.

# from unbalanced_dataset import UnderSampler, SMOTE, OverSampler
# np.random.seed(2244)
# ratio = float(np.count_nonzero(y==0)) / float(np.count_nonzero(y==1))

# sm = OverSampler(ratio=ratio)
# sm = SMOTE(k=5, m=2, kind='regular', verbose=True)

# print y.value_counts()
# train, y = sm.fit_transform(np.array(train),np.array(y))

# print pd.Series(y).value_counts()

# Modeling.

import xgboost as xgb

dtrain = xgb.DMatrix(train, label = y, missing = -1)
dtest = xgb.DMatrix(test, target_final, missing = -1)
watchlist = [(dtrain,'train'), (dtest,'test')]

params = {'objective':'binary:logistic', 'max_depth':7, 'eta':0.07, 'silent':1, 'subsample' : 0.6,# 'min_child_weight' : 1,
			'nthread':4, 'colsample_bytree':0.7, 'missing' : -1,  'scale_pos_weight': 3}

num_rounds = 110

def zoneEvalMetricXgB(predicted, dtrain, topTen=30):
	actual = dtrain.get_label()
	scores = pd.DataFrame({'actual':actual, 'predicted':predicted})
	scores.sort(columns='predicted', ascending=False, inplace=True)
	scores.reset_index(inplace = True)
	numerator = np.sum(scores.ix[0:int((float(topTen)*len(scores))/100), 'actual'])
	total = float(np.sum(scores['actual']))
	evalMetric = float(numerator)/total
	return 'metric', evalMetric * 100

def zoneEvalMetric(actual, predicted, topTen):
    scores = pd.DataFrame({'actual':actual, 'predicted':predicted})
    scores.sort(columns='predicted', ascending=False, inplace=True)
    scores.reset_index(inplace = True)
    numerator = np.sum(scores.ix[0:int((float(topTen)*len(scores))/100), 'actual'])
    total = float(np.sum(scores['actual']))
    evalMetric = float(numerator)/total
    return evalMetric * 100

params['seed'] = 0
bst1 = xgb.train(params, dtrain, num_rounds, watchlist, feval=zoneEvalMetricXgB)
# params['seed'] = 1111
# bst2 = xgb.train(params, dtrain, num_rounds, watchlist, feval=zoneEvalMetricXgB)
# params['seed'] = 2222
# bst3 = xgb.train(params, dtrain, num_rounds, watchlist, feval=zoneEvalMetricXgB)
# params['seed'] = 3333
# bst4 = xgb.train(params, dtrain, num_rounds, watchlist, feval=zoneEvalMetricXgB)
# params['seed'] = 4444
# bst5 = xgb.train(params, dtrain, num_rounds, watchlist, feval=zoneEvalMetricXgB)


test_preds1 = bst1.predict(dtest)
# test_preds2 = bst2.predict(dtest)
# test_preds3 = bst3.predict(dtest)
# test_preds4 = bst4.predict(dtest)
# test_preds5 = bst5.predict(dtest)

test_preds = np.mean((test_preds1), axis=0)

train_preds1 = bst1.predict(dtrain)
# train_preds2 = bst2.predict(dtrain)
# train_preds3 = bst3.predict(dtrain)
# train_preds4 = bst4.predict(dtrain)
# train_preds5 = bst5.predict(dtrain)

train_preds = np.mean((train_preds1), axis=0)

print "Test1 score:", zoneEvalMetric(target_final, test_preds1, 10)
# print "Test2 score:", zoneEvalMetric(target_final, test_preds2, 10)
# print "Test3 score:", zoneEvalMetric(target_final, test_preds3, 10)
# print "Test4 score:", zoneEvalMetric(target_final, test_preds4, 10)
# print "Test5 score:", zoneEvalMetric(target_final, test_preds5, 10)

print "Test1 score:", zoneEvalMetric(target_final, test_preds1, 30)
# print "Test2 score:", zoneEvalMetric(target_final, test_preds2, 30)
# print "Test3 score:", zoneEvalMetric(target_final, test_preds3, 30)
# print "Test4 score:", zoneEvalMetric(target_final, test_preds4, 30)
# print "Test5 score:", zoneEvalMetric(target_final, test_preds5, 30)

print "Test_ensemble Top - 10 score:", zoneEvalMetric(target_final, test_preds, 10)
print "Test_ensemble Top - 20 score:", zoneEvalMetric(target_final, test_preds, 20)
print "Test_ensemble Top - 30 score:", zoneEvalMetric(target_final, test_preds, 30)


print "Train1 score:", zoneEvalMetric(y, train_preds1, 10)
# print "Train2 score:", zoneEvalMetric(y, train_preds2, 10)
# print "Train3 score:", zoneEvalMetric(y, train_preds3, 10)
# print "Train4 score:", zoneEvalMetric(y, train_preds4, 10)
# print "Train5 score:", zoneEvalMetric(y, train_preds5, 10)

print "Train1 score:", zoneEvalMetric(y, train_preds1, 30)
# print "Train2 score:", zoneEvalMetric(y, train_preds2, 30)
# print "Train3 score:", zoneEvalMetric(y, train_preds3, 30)
# print "Train4 score:", zoneEvalMetric(y, train_preds4, 30)
# print "Train5 score:", zoneEvalMetric(y, train_preds5, 30)

print "Train_ensemble - Top 10 score:", zoneEvalMetric(y, train_preds, 10)
print "Train_ensemble - Top 20 score:", zoneEvalMetric(y, train_preds, 20)
print "Train_ensemble - Top 30 score:", zoneEvalMetric(y, train_preds, 30)

submit = pd.DataFrame({'id': ids_test, 'probability':test_preds, 'Success':target_final})
submit.to_csv("Finalprobs.csv", index = False)


#                        features  importance
# 3           RATIO_EOP_BAL_FEB15    0.045353
# 19                    SEP14_Bal    0.035617
# 83                 pl_holding_a    0.035310
# 23                    NOV14_Bal    0.035075
# 1                           AQB    0.033426
# 24                    NOV14_EOP    0.032853
# 25                    DEC14_Bal    0.032754
# 29                    FEB15_Bal    0.032658
# 27                    JAN15_Bal    0.032349
# 21                    OCT14_Bal    0.032286
# 30                    FEB15_EOP    0.031592
# 22                    OCT14_EOP    0.031213
# 20                    SEP14_EOP    0.031131
# 26                    DEC14_EOP    0.030819
# 85                 pl_holding_c    0.030369
# 2   Number_Balance_enquiries_3m    0.030248
# 28                    JAN15_EOP    0.030182
# 4                   DC_SPEND_3M    0.030125
# 5                   CC_SPEND_3M    0.028195
# 0                           AGE    0.023862
# 18                 salary_feb15    0.022193
# 17                 salary_jan15    0.020901
# 16                 salary_nov14    0.020320
# 15                 salary_oct14    0.017484
# 14                 salary_sep14    0.017455
# 7           Total_asset_holding    0.016579
# 13                 product_code    0.015397
# 33               Dmat_Investing    0.010909
# 32               RD_AMOUNT_BOOK    0.010644
# 41       COC_DAE_EASY_EMI_tag_N    0.008661
# ..                          ...         ...
# 38    Transactor_revolver_tag_N    0.002601
# 92                      event_N    0.002588
# 66          ratio_eop_amb_bin_d    0.002553
# 81                hnw_segment_b    0.002451
# 36    Transactor_revolver_tag_D    0.002435
# 55       Prematured_FD_Tag_3M_N    0.002420
# 34             Account_type_CSA    0.002363
# 73        balance_enquiry_bin_a    0.002347
# 56       Prematured_FD_Tag_3M_Y    0.002323
# 48                  PAPQ_Tag_PQ    0.002287
# 76        balance_enquiry_bin_d    0.002181
# 74        balance_enquiry_bin_b    0.002107
# 35              Account_type_SA    0.002070
# 70          ratio_eop_amb_bin_h    0.002050
# 59           closed_RD_Tag_3M_N    0.001918
# 50                CITY_CHANGE_Y    0.001910
# 67          ratio_eop_amb_bin_e    0.001899
# 61           closed_FD_Tag_3M_N    0.001897
# 51          Joint_account_tag_N    0.001870
# 52          Joint_account_tag_Y    0.001820
# 69          ratio_eop_amb_bin_g    0.001809
# 62           closed_FD_Tag_3M_Y    0.001751
# 49                CITY_CHANGE_N    0.001717
# 60           closed_RD_Tag_3M_Y    0.001634
# 54          CHQ_BOUNCE_TAG_3M_Y    0.001535
# 53          CHQ_BOUNCE_TAG_3M_N    0.001445
# 68          ratio_eop_amb_bin_f    0.001372
# 65          ratio_eop_amb_bin_c    0.000525
# 63          ratio_eop_amb_bin_a    0.000360
# 64          ratio_eop_amb_bin_b    0.000259



# [88]	test-auc:0.841064	train-auc:0.897911
# [89]	test-auc:0.841113	train-auc:0.898692
# [90]	test-auc:0.841356	train-auc:0.899177
# [91]	test-auc:0.841715	train-auc:0.899989
# [92]	test-auc:0.842159	train-auc:0.900909
# [93]	test-auc:0.842195	train-auc:0.901197
# [94]	test-auc:0.842321	train-auc:0.901914
# [95]	test-auc:0.842431	train-auc:0.902744
# [96]	test-auc:0.842443	train-auc:0.903364
# [97]	test-auc:0.842638	train-auc:0.904153
# [98]	test-auc:0.842991	train-auc:0.904884
# [99]	test-auc:0.842881	train-auc:0.905594
# [100]	test-auc:0.843099	train-auc:0.905982
# [101]	test-auc:0.843274	train-auc:0.906518
# [102]	test-auc:0.843193	train-auc:0.907391
# [103]	test-auc:0.843131	train-auc:0.908127
# [104]	test-auc:0.843154	train-auc:0.908959
# [105]	test-auc:0.843104	train-auc:0.909561
# [106]	test-auc:0.843318	train-auc:0.909962