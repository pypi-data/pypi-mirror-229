from research_framework.container.container import Container
from research_framework.lightweight.lightweight import FlyWeight
from research_framework.pipeline.model.pipeline_model import PipelineModel, FilterModel, InputFilterModel
from research_framework.pipeline.pipeline import FitPredictPipeline


test_pipeline = PipelineModel(
    name='pipeline para tests',
    train_input= 
        InputFilterModel(
            clazz='CSVPlugin',
            name='texts_depression_2018.csv',
            params={
                "filepath_or_buffer":"test/data/texts_depression_2018.csv",
                "sep": ",",
                "index_col": 0,
            },
        )
    ,
    test_input =
        InputFilterModel(
            clazz='CSVPlugin',
            name='texts_depression_2022.csv',
            params={
                "filepath_or_buffer":"test/data/texts_depression_2022.csv",
                "sep": ",",
                "index_col": 0,
            }
        )
    ,
    filters= [
        FilterModel(
            clazz="FilterRowsByNwords",
            params={
                "upper_cut": 100,
                "lower_cut": 10,
            }
        )
    ],
    metrics = [
        
    ]
)


def test_simple_pipeline():
    print(Container.BINDINGS)
    Container.fly = FlyWeight()
    pipeline = FitPredictPipeline(test_pipeline)
    pipeline.start()
    
    print("- Train data:")
    for item in test_pipeline.train_input.items:
        print(item)
        assert Container.fly.unset_item(item.hash_code)
        
    print("- Test data:")
    for item in test_pipeline.test_input.items:
        print(item)
        assert Container.fly.unset_item(item.hash_code)
    
    print("- Trained models:")
    for plugin_filter in pipeline.pipeline.filters:
        if not plugin_filter.item is None:
            print(plugin_filter.item)
            assert Container.fly.unset_item(plugin_filter.item.hash_code)