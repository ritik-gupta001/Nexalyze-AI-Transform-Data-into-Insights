"""
Example usage of the PRA Agent API
Demonstrates all major features
"""
import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def check_health():
    """Check API health"""
    print_section("Health Check")
    
    response = requests.get(f"{API_V1}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def example_text_analysis():
    """Example: Analyze news/text"""
    print_section("Example 1: News Sentiment Analysis")
    
    payload = {
        "query": "Analyze recent news about Microsoft and predict sentiment trend",
        "entity": "Microsoft",
        "time_range": "last_7_days"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    response = requests.post(
        f"{API_V1}/tasks/analyze-text",
        json=payload
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Task Created: {result['task_id']}")
        print(f"Status: {result['status']}")
        print(f"\nSummary: {result['summary'][:200]}...")
        
        if result.get('sentiment_summary'):
            sent = result['sentiment_summary']
            print(f"\nSentiment Analysis:")
            print(f"  Overall: {sent['overall']}")
            print(f"  Positive: {sent['positive']*100:.1f}%")
            print(f"  Neutral: {sent['neutral']*100:.1f}%")
            print(f"  Negative: {sent['negative']*100:.1f}%")
        
        if result.get('forecast'):
            print(f"\nForecast: {result['forecast']}")
        
        if result.get('report_url'):
            print(f"\n📄 Report: {result['report_url']}")
        
        if result.get('charts'):
            print(f"📊 Charts: {len(result['charts'])} generated")
        
        return result['task_id']
    else:
        print(f"❌ Error: {response.text}")
        return None


def example_document_analysis():
    """Example: Analyze document"""
    print_section("Example 2: Document Analysis")
    
    # Create a sample text file
    sample_doc = Path("sample_document.txt")
    sample_doc.write_text("""
    Research Paper: Machine Learning in Healthcare
    
    Abstract:
    This paper explores the application of machine learning algorithms in 
    healthcare diagnostics. We present a novel approach using deep neural 
    networks for early disease detection with 95% accuracy.
    
    Introduction:
    Healthcare is being transformed by artificial intelligence...
    
    Methodology:
    We collected data from 10,000 patients and applied CNN models...
    
    Results:
    Our model achieved 95% accuracy, 93% precision, and 94% recall...
    
    Conclusion:
    Machine learning shows great promise in healthcare diagnostics.
    """)
    
    print(f"Document: {sample_doc}")
    print("Instruction: Summarize key findings and methodology\n")
    
    with open(sample_doc, 'rb') as f:
        files = {'file': (sample_doc.name, f, 'text/plain')}
        data = {'instruction': 'Summarize the key findings, methodology, and results'}
        
        print("Sending request...")
        response = requests.post(
            f"{API_V1}/tasks/analyze-doc",
            files=files,
            data=data
        )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Task Created: {result['task_id']}")
        print(f"Status: {result['status']}")
        print(f"\nAnalysis: {result['summary'][:300]}...")
        
        if result.get('report_url'):
            print(f"\n📄 Report: {result['report_url']}")
        
        return result['task_id']
    else:
        print(f"❌ Error: {response.text}")
        return None
    finally:
        # Clean up
        if sample_doc.exists():
            sample_doc.unlink()


def example_data_analysis():
    """Example: Analyze CSV data"""
    print_section("Example 3: Data Analysis")
    
    # Create sample CSV
    import pandas as pd
    
    sample_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'sales': [100 + i * 2 + (i % 10) * 10 for i in range(100)],
        'region': ['North', 'South', 'East', 'West'] * 25,
        'product': ['A', 'B', 'C'] * 33 + ['A']
    })
    
    csv_file = Path("sample_data.csv")
    sample_data.to_csv(csv_file, index=False)
    
    print(f"Dataset: {csv_file}")
    print(f"Shape: {sample_data.shape}")
    print("Instruction: Find patterns and trends in sales data\n")
    
    with open(csv_file, 'rb') as f:
        files = {'file': (csv_file.name, f, 'text/csv')}
        data = {'instruction': 'Find patterns, trends, and anomalies in sales data'}
        
        print("Sending request...")
        response = requests.post(
            f"{API_V1}/tasks/analyze-data",
            files=files,
            data=data
        )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Task Created: {result['task_id']}")
        print(f"Status: {result['status']}")
        print(f"\nAnalysis: {result['summary'][:300]}...")
        
        if result.get('metadata'):
            meta = result['metadata']
            print(f"\nDataset Info:")
            print(f"  Rows: {meta.get('rows', 'N/A')}")
            print(f"  Columns: {meta.get('columns', 'N/A')}")
        
        if result.get('report_url'):
            print(f"\n📄 Report: {result['report_url']}")
        
        if result.get('charts'):
            print(f"📊 Charts: {len(result['charts'])} generated")
        
        return result['task_id']
    else:
        print(f"❌ Error: {response.text}")
        return None
    finally:
        # Clean up
        if csv_file.exists():
            csv_file.unlink()


def get_task_status(task_id):
    """Get task status"""
    print_section(f"Get Task Status: {task_id}")
    
    response = requests.get(f"{API_V1}/tasks/{task_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nTask ID: {result['task_id']}")
        print(f"Status: {result['status']}")
        print(f"Created: {result['created_at']}")
        print(f"Completed: {result.get('completed_at', 'N/A')}")
    else:
        print(f"❌ Error: {response.text}")


def list_all_tasks():
    """List all tasks"""
    print_section("List All Tasks")
    
    response = requests.get(f"{API_V1}/tasks/?page=1&page_size=5")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nTotal Tasks: {result['total']}")
        print(f"Page: {result['page']} (showing {result['page_size']} per page)")
        print(f"\nRecent Tasks:")
        
        for task in result['tasks']:
            print(f"\n  Task ID: {task['task_id']}")
            print(f"  Status: {task['status']}")
            print(f"  Summary: {task['summary'][:100]}...")
    else:
        print(f"❌ Error: {response.text}")


def main():
    """Run all examples"""
    print("\n" + "🧠 PRA - Personal Research Agent".center(60))
    print("Example Usage Demonstration".center(60))
    print("")
    
    # Check if API is running
    if not check_health():
        print("\n❌ API is not running. Please start the server first:")
        print("   python -m app.main")
        return
    
    print("\n✅ API is running and healthy!")
    
    # Run examples
    task_ids = []
    
    # Example 1: Text Analysis
    task_id = example_text_analysis()
    if task_id:
        task_ids.append(task_id)
    
    input("\nPress Enter to continue to next example...")
    
    # Example 2: Document Analysis
    task_id = example_document_analysis()
    if task_id:
        task_ids.append(task_id)
    
    input("\nPress Enter to continue to next example...")
    
    # Example 3: Data Analysis
    task_id = example_data_analysis()
    if task_id:
        task_ids.append(task_id)
    
    input("\nPress Enter to view task status...")
    
    # Get task status for first task
    if task_ids:
        get_task_status(task_ids[0])
    
    input("\nPress Enter to list all tasks...")
    
    # List all tasks
    list_all_tasks()
    
    print_section("Examples Complete!")
    print("Check the following directories for outputs:")
    print("  📄 Reports: app/reports/")
    print("  📊 Charts: app/charts/")
    print("  📝 Logs: logs/pra.log")
    print("\nVisit http://localhost:8000/docs for interactive API documentation")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Examples interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
