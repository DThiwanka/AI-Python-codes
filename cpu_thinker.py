import time
import random
import threading
import queue
import psutil
from transformers import pipeline

# Configuration
NUM_CORES = psutil.cpu_count(logical=False)  # Physical CPU cores
QUESTION_GENERATION_TIME_MIN = 1  # Minimum time to generate a question (seconds)
QUESTION_GENERATION_TIME_MAX = 5  # Maximum time to generate a question (seconds)
INFERENCE_TIME_MIN = 2         # Minimum time for inference (seconds)
INFERENCE_TIME_MAX = 10        # Maximum time for inference (seconds)
QUEUE_SIZE = 20                # Size of the task queue.  Smaller than before because transformers are memory intensive.

# Initialize the question generation pipeline.
question_generator = pipeline("text-generation", model="gpt2") # Use a simpler model

# Initialize the question answering pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")


def generate_question(task_id):
    """Simulates generating a question."""
    generation_time = random.uniform(QUESTION_GENERATION_TIME_MIN, QUESTION_GENERATION_TIME_MAX)
    start_time = time.time()

    # Use a placeholder for actual question generation logic.  The model call below IS the question generation.
    # Replace with your question generation model or method.  This is just a simulation
    # to burn some CPU time while we pretend to be thinking up a question.
    while time.time() - start_time < generation_time:
       pass # CPU bound wait

    prompt = "What is the meaning of life, the universe, and everything?"
    generated_question = question_generator(prompt, max_length=50, num_return_sequences=1)[0]['generated_text']

    print(f"Task {task_id}: Generated question: {generated_question} after {generation_time:.2f} seconds")
    return generated_question

def answer_question(question, task_id):
    """Simulates answering a question using a QA model."""
    inference_time = random.uniform(INFERENCE_TIME_MIN, INFERENCE_TIME_MAX)
    start_time = time.time()

    # Replace with your question answering model or method.  This is just a simulation
    # to burn some CPU time while we pretend to be answering.
    context = "The meaning of life, the universe, and everything is 42, according to a supercomputer called Deep Thought."
    result = qa_pipeline(question=question, context=context)


    while time.time() - start_time < inference_time:
        pass # CPU bound wait

    print(f"Task {task_id}: Answered question after {inference_time:.2f} seconds.  Answer: {result['answer']}, Score: {result['score']:.2f}")
    return result['answer']

def worker(queue, worker_id):
    """Worker thread that pulls tasks from the queue, generates a question, answers it, and executes them."""
    while True:
        task_id = queue.get()
        if task_id is None:  # Sentinel value to stop the worker
            print(f"Worker {worker_id} exiting.")
            queue.task_done()
            break

        try:
            question = generate_question(task_id)
            answer = answer_question(question, task_id)
            print(f"Worker {worker_id}:  Task {task_id} completed. Answer: {answer}")

        except Exception as e:
            print(f"Worker {worker_id}: Error processing task {task_id}: {e}")
        finally:
            queue.task_done() # signal that the current task is done

def main():
    """Main function to create tasks, distribute them to workers, and manage the queue."""
    task_queue = queue.Queue(maxsize=QUEUE_SIZE)

    # Create and start worker threads
    workers = []
    for i in range(NUM_CORES):
        worker_thread = threading.Thread(target=worker, args=(task_queue, i + 1), daemon=True)
        workers.append(worker_thread)
        worker_thread.start()

    # Generate tasks (simulated "ideas" or "problems")
    num_tasks = 10
    for i in range(num_tasks):
        task_queue.put(i + 1)  # Task ID

    print(f"Submitted {num_tasks} tasks to the queue.")

    # Wait for all tasks to be processed
    task_queue.join()  # Block until all items in the queue have been gotten and processed

    # Signal workers to stop
    for _ in range(NUM_CORES):
        task_queue.put(None)  # Add sentinel values to stop workers

    # Wait for workers to exit
    for worker_thread in workers:
        worker_thread.join()

    print("All tasks completed and workers finished.")


if __name__ == "__main__":
    print(f"Running with {NUM_CORES} CPU cores.")
    main()