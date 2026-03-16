import sys
import os
import asyncio

# Disable proxy
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

# Add project root to python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from google.adk.evaluation.agent_evaluator import AgentEvaluator

async def main():
    test_folder = os.path.dirname(__file__)
    test_file = os.path.join(test_folder, "companies_house_agent.test.json")
    agent_module_name = "companies_house_agent.agent"
    
    from google.adk.evaluation.metric_evaluator_registry import DEFAULT_METRIC_EVALUATOR_REGISTRY
    print(f"Registered metrics in DEFAULT: {[m.metric_name for m in DEFAULT_METRIC_EVALUATOR_REGISTRY.get_registered_metrics()]}")
    
    try:
        await AgentEvaluator.evaluate(
            agent_module=agent_module_name,
            eval_dataset_file_path_or_dir=test_file,
            num_runs=1,
            print_detailed_results=True,
        )
        print("Evaluations completed successfully.")
    except Exception as e:
        print(f"Error running evaluations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
