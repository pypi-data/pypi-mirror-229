## AIBridge 0.0.1

AIBridge is the python package with the support of the Multiple LLM's,User can utilised the Formatters ,prompts, varibales to get most of the LLM's Through the AIBridge

### Requirement

- Python 3

### Install The Test package

```python
pip install aibridge-test
```

### Set config.yaml

- Setting the the config.yaml at your desire choice
- In .env file set the path for file.

```python
Example in bash we set:
export AIBRIDGE_CONFIG=C:/Users/Admin/aibridge/config.yaml
variable name for env:AIBRIDGE_CONFIG
```

```python
starter file.
group_name: consumer gorup name
message_queue: redis
no_of_threads: 1
open_ai:
- key: Api_key
  priority: equal
- key: APi_key
  priority: equal
redis_host: localhost
redis_port: port _for redis
stream_name: redis topic
```

### Configuration

- With the help of the AIBridge we can svae the prompts in your sql/nosql data bases by default the :sqllite on the disc space
- To configure the database you have add the data in config file.

```python
from AIBridge impprt Setconfig
#call the config method
Setconfig.set_db_confonfig(database=sql,database_name=None,database_uri=None)
#parameters:
#database-sql/nosql
#database_uri: url of the databse of your choice(all sql support for no sql(Mongo))
```

- If you want use the sqllite on the disc no need to configure these for db support
- Currently AI bridge support only the OPEN_AI api:

```python
from AIBridge import SetConfig
SetConfig.set_api_key(ai_service="open_ai",key="YOUR_API_KEY",priority="high")
#priority:high/medium/low/equal
```

### Prompt save

- Prompt save mechanism is used the save the reusable and extraordinary prompts that give you the exceptional result from LLM

```python
from AIBridge import PromptInsertion

# save prompt
data = PromptInsertion.save_prompt(
    prompt="your prompt:{{data}},context:{{context}}",
    name="first_prompt",
    prompt_data={"data": "what is purpose of the ozone here"},
    variables={"context": "environment_context"},
)
print(data)
# parameters: prompt_data: is used to manipulatre the same prompt  with diffrent context at realtime
# variables: is used to manipulate the prompt with fixed context as varibales is a specific data


#update prompt can see the prompt_data and variables, is used the get diffrent output from same prompt
data = PromptInsertion.update_prompt(
    id="prompt_id",
    name="updated_prompt",
    prompt_data={"data": "write abouts the plastic pollution"},
    variables={"context": "ocean_pollution"},
)
print(data)


#Get prompt from id
data = PromptInsertion.get_prompt(id="prompt_id")
print(data)

# pagination support for getting the all prompt
data = PromptInsertion.get_all_prompt(page=1)
print(data)
```

### variables

- why variables?-> variables are the specific data used the get the desired and with context from ai LLM's.
- These is the example of the self consistance prompts Ref:https://www.promptingguide.ai/techniques/consistency
- Varibales methods:

```python
from AIBridge import VariableInsertion

# save varibales
# parameters: var_key: key for the varibales
# var_value: list of the string for the context
data = VariableInsertion.save_variables(
    var_key="ochean_context",
    var_value=[
        "Ocean pollution is a significant environmental issue that poses a threat to marine life and ecosystems"
    ],
)
print(data)

# update the variables
data = VariableInsertion.update_variables(
    id="variable_id",
    var_key="updated_string",
    var_value=["updated senetece about topics"],
)
print(data)

# get Variables from id
data = VariableInsertion.get_variable(id="variable_id")

# get all Variables pagination
data = VariableInsertion.get_all_variable(page=1)

```

### Get Response

- LLm=open_ai
- default_model="gpt-3.4-turbo-oo3"
- Max_toke count - 3500
- temprature set to 0.5
  methods

```python
from AIBridge import OpenAIService
import json

json_schema = json.dumps({"animal": ["list of animals"]})
xml_schema = "<animals><category>animal name</category></animals>"
csv = "name,category,species,age,weight,color,habitat"
data = OpenAIService.generate(
    prompts=["name of the animals in the  {{jungle}}"],
    prompt_ids=None,
    prompt_data=[{"jungle": "jungle"}],
    variables=None,
    output_format=["json"],
    format_strcture=[json_schema],
    model="gpt-3.5-turbo",
    variation_count=1,
    max_tokens=3500,
    temperature=0.5,
    message_queue=False,
)
print(data)
# Prameters
# prompts= list of the string that need to executed in session  where output id dependant on each other,
# promts_ids= prompt  id's list and  so at a time ids will execute or prompts,
# prompt_data=[data of the every prompt id they required],
# variables=[ varibale dict of the prompt],
# output_format=["xml/json/csv/sql/"],
# format_strcture=[out put strcture of the prompt],
# model="gpt-3.5-turbo", model for completion api of the gpt
# variation_count = 1,  n of the output require
# max_tokens = 3500, maximut token per out put
# temperature = 0.5, data consistecy
# message_queue=False, scalability purpose

output = {
    "items": {
        "response": [
            {
                "data": [
                    '{"animal": ["lion", "tiger", "elephant", "monkey", "snake", "gorilla", "leopard", "crocodile", "jaguar", "giraffe"]}'
                ]
            }
        ],
        "token_used": 85,
        "created_at": 1689323114.9568439,
        "ai_service": "open_ai",
    }
}

```

### Message Queue

- default Queue=redis,

#### Configure redis

```python
from AIBridge import SetConfig
# set redis configuration
SetConfig.redis_config(
    redis_host="localhost",
    redis_port="port _for redis",
    group_name="consumer gorup name",
    stream_name="redis topic",
    no_of_threads=1,#concurrent thread ypu want run for your application
)
```

- To use the Queue service set message_queue = True

```python
from AIBridge import OpenAIService
import json

json_schema = json.dumps({"animal": ["list of animals"]})
data = OpenAIService.generate(
    prompts=["name of the animals in the  {{jungle}}"],
    prompt_ids=None,
    prompt_data=[{"jungle": "jungle"}],
    variables=None,
    output_format=["json"],
    format_strcture=[json_schema],
    message_queue=True# to activate message queue service
)
# to use the Queue service use the name set the message queue prameter = True
print(data)
```

\*Response for above function is the id of the response stored in the databse

```json
{ "response_id": "eaa61944-3216-4ba1-bec5-05842fb86d86" }
```

- Message queue is for increasing scalibilty
- for APplication server you have turn on the consumer when application getting started.

```python
from AIBridge import MessageQ

# to start the consumer in background
MessageQ.mq_deque()
```

- In the non application environmen:
  - you can run set message queue=True
- Run the below function to procees the Stream data in consumer

```python
from AIBridge import MessageQ
# these for testingthe redis env in local on single page file
data = MessageQ.local_process()
print(data)
```

###Dalle image genration###

```python
from AIBridge.ai_services.openai_images import OpenAIImage

images = OpenAIImage.generate(
    prompts=["A sunlit indoor lounge area with a pool containing a flamingo"],
    image_data=["image loacation or image url"],
    mask_image=["image loacation or image url"],
    variation_count=1,
    process_type="edit",
)
print(images)

# prompts: is list string how many diffrent image we have to genearte
# image_data: is the lacation of the image in file or the image url
# mask_image: is the mask image with transpernet patch in the  image where we want edit the images
# variation_count: is the number of image we want to generate
# prcess type : create, edit, variation,
# create is for genrating new images
# edit the image with the mask mask is compulsary to edi the images
# variation is for genrating new images of sama type

```

###Palm-Text APi Integration###

- To set APi key in confif.yaml file you can add the it directly in config.yaml file in the format

```yaml
   palm_api:
  - key: AIz****************************QkkA(your-api_key)
    priority: equal
```

```python
    from AIBridge import SetConfig
    SetConfig.set_api_key(ai_service="palm_api",key="YOUR_API_KEY",priority="high")
    #priority:high/medium/low/equal
```

````
```python
from AIBridge import PalmText

prompt = """
write paragraph about the {{prompting}}in ai and let user know what is the{{prompting}} and how the {{prompting}} works in genrative AI
"""
json_format = """{"text": "paragraph here"}"""
data = PalmText.generate(
    prompts=[prompt],
    prompt_data=[{"prompting": "model training"}],
    output_format=["json"],
    format_strcture=[json_format],
    message_queue=True,
)
print(data)
# Prameters
# prompts= list of the string that need to executed in session  where output id dependant on each other,
# promts_ids= prompt  id's list and  so at a time ids will execute or prompts,
# prompt_data=[data of the every prompt id they required],
# variables=[ varibale dict of the prompt],
# output_format=["xml/json/csv/sql/"],
# format_strcture=[out put strcture of the prompt],
# model="models/text-bison-001", model for generate api of the palm
# variation_count = 1-8,  n of the output require
# max_tokens = default 10000, maximut token per out put, no limit for token"
# temperature = default-0.5, data consistecy
# message_queue=False, scalability purpose
````

### Palm CHAT- API###

```python
    from AIBridge import PalmChat
    # An array of "ideal" interactions between the user and the model
    examples = [
        (
            "What's up?",
            "What isn't up?? The sun rose another day, the world is bright, anything is possible!",
        ),
        (
            "I'm kind of bored",
            "How can you be bored when there are so many fun, exciting, beautiful experiences to be had in the world?",
        ),
    ]
    data = PalmChat.generate(
        messages="give the protype for the stack on c++",
        context="carreer or growth advides",
        variation_count=3,
        message_queue=True,
    )
    print(data)
    # mesages: text provided to chat
    # context: on the what basis do you want start the chat
    # examples: demo for the LLm to undersat the tone and what do you reaaly want(few shot prompt type)
    # variation_count: how many variations of the context should be used
    # message_queue: if true, the chat will return the messages in a queue
    # temperature = default-0.5, data consistecy
```
