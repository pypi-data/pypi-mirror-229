'''
Labeling generation tools. 
'''  
def SimpleThresoldingLambdaGenerator(feature_tuple_list, function_names = None, return_type = dict):
    '''
    Creates a simple thresholding lambda function base on the key-value pairs feature_tuple_list. 
    
    feature_tuple_list : Feature name as fist value of tuple, threshold as second. 
                   If a tuple of two features is provided as key, 
                   threshold will be applied on the difference of the two. 
                   Examples:
                   [('ft', 'th'),
                   ('ft': ('th', 'over')),
                   (('ft1', 'ft2'): th),
                   (('ft1', 'ft2'): ('th', 'over'))]
                   
    function_names : List of name of the lambda functions. Ordered list is assumed.
    return_type : Returns function dict when set to 'dict'. Returns list of functions when set to list
    '''
    
    lambda_functions = []
    for (feature, threshold) in feature_tuple_list:
        if isinstance(feature, str):
            if isinstance(threshold, (int, float)):
                lambda_fn = lambda x, feature=feature, threshold=threshold: getattr(x, feature) >= threshold
            elif isinstance(threshold, tuple) and len(threshold) == 2:
                if threshold[1] == 'over':
                    lambda_fn = lambda x, feature=feature, threshold=threshold: getattr(x, feature) >= threshold[0]
                elif threshold[1] == 'under':
                    lambda_fn = lambda x, feature=feature, threshold=threshold: getattr(x, feature) < threshold[0]
                else:
                    raise ValueError("Invalid thresolding operator. When tuple is provided second element must be either 'over' or 'under'.")
            else:
                raise ValueError("Invalid value in feature_tuple_list thresholding.")
        elif isinstance(feature, tuple) and len(feature) == 2:
            if isinstance(threshold, (int, float)):
                lambda_fn = lambda x, feature1=feature[0], feature2=feature[1], threshold=threshold: getattr(x, feature1) - getattr(x, feature2) >= threshold
            elif isinstance(threshold, tuple) and len(threshold) == 2:
                if threshold[1] == 'over':
                    lambda_fn = lambda x, feature1=feature[0], feature2=feature[1], threshold=threshold: getattr(x, feature1) - getattr(x, feature2) >= threshold[0]
                elif threshold[1] == 'under':
                    lambda_fn = lambda x, feature1=feature[0], feature2=feature[1], threshold=threshold: getattr(x, feature1) - getattr(x, feature2) < threshold[0]
                else:
                    raise ValueError("Invalid thresolding operator. When tuple is provided second element must be either 'over' or 'under'.")
            else:
                raise ValueError("Invalid value in feature_tuple_list thresholding.")       
        else:
            raise ValueError("Invalid key in feature_tuple_list. Must be a string or a tuple of two strings.")
        lambda_functions.append(lambda_fn)
    if function_names is None:
        function_set = {'label_fn_{}'.format(idx+1): fn for idx, fn in enumerate(lambda_functions)}
    else:
        function_set = {fn_name: fn for fn_name, fn in zip(function_names, lambda_functions)}
    if return_type == dict:
        return function_set
    else:
        return lambda_functions

def LambdaFunctionGrouper(fn_list, operation):
    '''
    Returns one lambda function which groups all provided lambda functions in the fn_list.  
    
    fn_list : List of lambda functions to group.  
    operation : Logical operator to use while grouping. (and, or, xor)
    ''' 
    if operation == 'and':
        return lambda x: pd.concat([fn(x) for fn in fn_list], axis=1).all(axis=1)
    elif operation == 'or':
        return lambda x:  pd.concat([fn(x) for fn in fn_list], axis=1).any(axis=1)
    elif operation == 'xor':
        return lambda x: pd.concat([fn(x) for fn in fn_list], axis=1).sum(axis=1) % 2 == 1
    else:
        raise ValueError("Invalid operation. Supported operations are 'and', 'or', and 'xor'.")


def LabelFeatureGenerator(base_data, function_set, unique_id = None):
    '''
    Returns a pandas dataframe with labels generated as per function_set. Output is indexed at unique_id if provided else maintains index order of base_data.
    Uses pandas assign() method to execute which takes a similar apprach as applymap() or apply() operations. 
    
    base_data : Pandas dataframe to apply the methods in function set. 
    function_set : Dictionary where key is string and value contains a function with one input variable. 
                   Key would be used to name the new column created. 
    unique_id : Unique row identifier to be used for indexing data. Default index used when left "None"
    '''
    
    data_w_lable = base_data.assign(**function_set)
    if unique_id != None:
        data_w_lable = data_w_lable.set_index(unique_id)
    generated_label_cols = [col for col in data_w_lable.columns if col not in base_data.columns]
    data_w_lable[generated_label_cols] = data_w_lable[generated_label_cols].fillna(0).astype(int)
    return data_w_lable[generated_label_cols]

def CalcCoverageStats(data, label_column, GT_column, GT_th_col,_print_ = True):
    '''
    Returns performance stats of label_column over GT_column for metric stats and GT_th_col for count stats.
    
    data: Pandas dataframe
    label_column: label to measure performance of. 
    GT_column: Ground trith column in the data. 
    GT_th_col: Binary Ground truth column in the data.
    _print_: Print stats when True.
    
    '''
    pred_len = sum(data[label_column]>0)
    
    GT_pred =  round(data[(data[label_column]>0) ][GT_column].sum()/1000000)
    GT_tot = round(data[GT_column].sum()/1000000)
    
    cov_ratio = round(data[(data[label_column]>0) ][GT_column].sum()/ data[GT_column].sum(), 2)*100
    
    tp_GT_col = round(data[(data[GT_th_col] == 1) & (data[label_column] > 0 )][GT_column].sum()/1000000)
    fp_GT_col = round(data[(data[GT_th_col] == 0) & (data[label_column] > 0 )][GT_column].sum()/1000000)
    fn_GT_col = round(data[(data[GT_th_col] == 1) & (data[label_column] == 0 )][GT_column].sum()/1000000)
    
    tp_GT_cnt = data[(data[GT_th_col] == 1) & (data[label_column] > 0 )].shape[0]
    fp_GT_cnt = data[(data[GT_th_col] == 0) & (data[label_column] > 0 )].shape[0]
    fn_GT_cnt = data[(data[GT_th_col] == 1) & (data[label_column] == 0 )].shape[0]
    
    try:
        cnt_pr = tp_GT_cnt/(tp_GT_cnt+fp_GT_cnt)
        cnt_re = tp_GT_cnt/(tp_GT_cnt+fn_GT_cnt)
        
        rev_pr = tp_GT_col/(tp_GT_col+fp_GT_col)
        rev_re = tp_GT_col/(tp_GT_col+fn_GT_col)
    except:
        cnt_pr, cnt_re, rev_pr, rev_re = 0, 0, 0, 0
        
    if _print_ == True: 
        print('GT Pred: ',GT_pred, '\n', 'GT total: ', GT_tot)
        
        print('GT $ Coverage Precision: ', round(rev_pr ,3)*100, '%')
        print('GT $ Coverage Recall: ', round(rev_re ,3)*100, '%')
        print('Coverage Recall: ', cov_ratio, '%')
        
        print('GT Cust-Cnt Precision: ', round(cnt_pr ,3)*100, '%')
        print('GT Cust-Cnt Recall: ', round(cnt_re ,3)*100, '%')
        
    return label_column, GT_pred, GT_tot, cov_ratio, cnt_pr, cnt_re, rev_pr, rev_re, tp_GT_cnt

def GetLabelCoverageStats(base_data, weak_labels, unique_id,  truth_col , truth_col_th , __print__ = False):
    '''
    Returns stats for label performance on a specified column in the base_data. 
    
    base_data: Pandas dataframe
    weak_labels: Label columns with unique id 
    unique_id: Id column that is present in both the datasets. To be used for a merge. 
    truth_col: Column in the base_data to be measure performance on. 
    truth_col_th: Use if truth_col is not binary. Any value greater than truth_col_th would be 1 and others 0.
    __print__: Will print stats for each label in weak_labels dataset when set to "True".
    '''
    
    merge_data = base_data.merge(weak_labels, on = unique_id, how = 'left').fillna(0)
    label_columns = [col for col in weak_labels.columns if col != unique_id]
    if truth_col_th == None: 
        assert merge_data[truth_col].nunique() == 2, 'Truth Column has more than 2 unique values. Provide a threshold to covert it to binary.'
    else:
        merge_data['_GT_'] = np.where(merge_data[truth_col] >= truth_col_th, 1, 0)
    
    stat_lst = []
    for col in label_columns:
        label_col, truth_pred, truth_tot, cov_ratio, cnt_pr, cnt_re, rev_pr, rev_re, _tp_cnt_ = CalcCoverageStats(merge_data, col, 
                                                                                                                  truth_col, '_GT_',
                                                                                                                  _print_ = __print__)
        
        
        stat_lst.append([label_col, truth_pred, truth_tot, cov_ratio, cnt_pr, cnt_re, rev_pr, rev_re, _tp_cnt_])
    stat_dt = pd.DataFrame(stat_lst)
    stat_dt.columns = ['Weak Label', 'GT Predicted(*1e6)', 'GT Total(*1e6)', 'Coverage Ratio', 'Count Precision', 'Count Recall', 'Metric Precision',
                      'Metric Recall', 'TP Predicted ']
    return stat_dt
#import inspect
#lines = inspect.getsource(ls[0])
#print(lines)