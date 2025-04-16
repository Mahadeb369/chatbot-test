import openai
import os
import time
from flask import current_app as app

api_key = os.getenv("OPEN_AI_API_KEY") or ""
client = openai.OpenAI(api_key=api_key)

STATIC_FOLDER = '/app/static'
os.makedirs(STATIC_FOLDER, exist_ok=True)
app.config['STATIC_FOLDER'] = STATIC_FOLDER


GRAPH_DETECTION_PROMPT = """
    Analyze if the user query explicitly requests any graphical representation. 
    Consider these as positive indicators:
    - Any mention of: graph, chart, diagram, plot, visualization, venn, histogram, bar, pie, line, scatter, etc.
    - Specific requests for visual representations or data plotting
    
    Respond ONLY with "True" if graph-related terms are found, otherwise "False".

    Here's is the user query:
    **User Query**: "{user_prompt}"
  """

ONLY_GRAPH_DETECTION_PROMPT = """
    Analyze if the user query SOLELY requests visualization based on previous data, without requesting new information.
    
    Return "True" if AND ONLY if:
    - The query ONLY requests visualization (graph, chart, diagram, etc.)
    - The query does NOT ask for any new data or information gathering
    
    Key patterns to check:
    1. If the query asks for both information AND visualization in the same request, return "False"
    2. If the query uses phrases like "also generate graph" but after requesting new information, return "False"
    3. If the query contains sentences requesting data collection before visualization, return "False"
    
    Examples that should return "True":
    - "Based on the previous response, generate a graph"
    - "For the above data, create a bar chart"
    - "Also, give me the venn diagram." (standalone request)
    - "Can you visualize this data?" (standalone request)
    
    Examples that should return "False":
    - "Show me the vacant site present at Bangalore airport, also show me its visualization"
    - "Show the vacant high street sites at all airports. Also generate graph."
    - "Show the occupancy percentage of digital arcade on DIAL."
    
    Critically analyze if ANY information gathering is requested alongside visualization.
    
    Respond ONLY with "True" or "False".
    
    User query to analyze:
    "{user_prompt}"
    """

def generate_graphs(csv_path, user_query):
  """
  Generate visualizations using Matplotlib and Seaborn based on the user query and structured csv data.
  Args:
  - csv_path (str): Path to the structured csv data file.
  - user_query (str): User query to analyze the data.
  Returns:
  - str: Generated visualizations and insights.
  """

  if csv_path == None:
    return []

  file = client.files.create(
    file=open(f"{csv_path}", "rb"),
    purpose='assistants'
  )

  assistant = client.beta.assistants.create(
    instructions="You are an expert in Python data visualization. Your task is to generate a **single visualization** using Matplotlib and Seaborn based on the user query and the provided CSV data, Firsly generate the best possible visualizations using Matplotlib and Seaborn. Ensure readability, clarity, and usefulness in the graphs. Remember you have to consider every data in the csv.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
    tool_resources={
      "code_interpreter": {
        "file_ids": [file.id]
      }
    }
  )

  your_query = f"{user_query}"
  user_prompt = f"""
  User Query: "{your_query}"

  Task:
  - Analyze the given data on the basis of User Query.
  - Identify the best visualization(s) for the dataset.
  - **If a specific graph type is mentioned, strictly generate that type.**
  - Choose best possible graph to visualize the data (e.g., Bar graph, Histrogram, Pie-Chart, Venn-Diagram)
  - Generate a Python script using Matplotlib and Seaborn.
  - Ensure clear labeling, color distinction, and readability.
  - Execute the code using the Assistant's Code Interpreter.
  **IMPORTANT** - DO NOT miss any data from the csv, show visualization considering every single data.
  **Return only ONE image—do NOT generate multiple visualizations.**

  Expected Output:
  - The executed visualization results.
  """

  thread = client.beta.threads.create()
  thread_id = thread.id  # Save thread ID

  user_message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=user_prompt
  )

  run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant.id,
    instructions="Process the given data and generate visualizations. Use Python with Matplotlib/Seaborn and execute the script."
  )

  while run.status not in ["completed", "failed"]:
    time.sleep(3)
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

  # Retrieve the generated response from Assistant
  messages = client.beta.threads.messages.list(thread_id=thread_id)

  # Extract and Display Assistant's Response
  result = []
  # import pdb; pdb.set_trace()
  try:
    for message in messages:
      if message.role == "assistant":
        for item in message.content:
          print("type of response: ", type(item))
          if item.image_file:
            file_id = item.image_file.file_id
            file_content = client.files.content(file_id)
            # Define local file name
            local_filename = os.path.join(STATIC_FOLDER, f"{file_id}.png")
            # Save the image locally
            with open(local_filename, "wb") as f:
                f.write(file_content.content)
            
            result.append(local_filename.replace("/app", ""))
            
  except Exception as e:
    print(f"Error in gpt-visual: {e}")

  return result

def detect_graph_request(user_prompt):
  """Detects if user prompt requests any type of graph/chart visualization."""

  graph_detect_prompt = GRAPH_DETECTION_PROMPT.format(user_prompt = user_prompt)

  try:

    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[{"role": "system", "content": graph_detect_prompt}],
      max_tokens=500,
    )
    answer = response.choices[0].message.content.strip().lower()
    print("detect_graph_request: ", answer)
    return answer == "true"
  except Exception as e:
    print("Error in graph detection:", e)
    return False
  

def only_detect_graph_request(user_prompt):
    """Detects if user prompt requests any type of graph/chart visualization."""

    graph_detect_prompt = ONLY_GRAPH_DETECTION_PROMPT.format(user_prompt = user_prompt)

    try:

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": graph_detect_prompt}],
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip().lower()
        print("only_detect_graph_request: ",answer)
        return answer == "true"
    except Exception as e:
        print("Error in graph detection:", e)
        return False