from typing import Dict, Any, List
from datetime import datetime
import json

class ReportGenerator:
    def __init__(self):
        self.report_template = {
            'processing_summary': {},
            'data_quality': {},
            'api_results': {},
            'errors': {},
            'recommendations': [],
            'metadata': {}
        }
    
    def generate_processing_summary(self, total_rows: int, successful_rows: int, 
                                  failed_rows: int, processing_time: float) -> Dict[str, Any]:
        """Generate processing summary"""
        success_rate = (successful_rows / total_rows * 100) if total_rows > 0 else 0
        
        return {
            'total_rows': total_rows,
            'successful_rows': successful_rows,
            'failed_rows': failed_rows,
            'success_rate': round(success_rate, 2),
            'processing_time_seconds': round(processing_time, 2),
            'rows_per_second': round(total_rows / processing_time, 2) if processing_time > 0 else 0
        }
    
    def generate_data_quality_metrics(self, transformed_data: List[Dict], 
                                    validation_errors: List[Dict]) -> Dict[str, Any]:
        """Generate data quality metrics"""
        if not transformed_data:
            return {
                'completeness_score': 0,
                'validity_score': 0,
                'quality_issues': []
            }
        
        # Calculate completeness
        total_fields = len(transformed_data[0]) if transformed_data else 0
        filled_fields = 0
        total_possible_fields = total_fields * len(transformed_data)
        
        for row in transformed_data:
            filled_fields += sum(1 for value in row.values() if value and str(value).strip())
        
        completeness_score = (filled_fields / total_possible_fields * 100) if total_possible_fields > 0 else 0
        
        # Calculate validity
        validation_error_count = len([e for e in validation_errors if e.get('type') == 'validation_error'])
        validity_score = ((len(transformed_data) - validation_error_count) / len(transformed_data) * 100) if transformed_data else 0
        
        # Identify quality issues
        quality_issues = []
        if completeness_score < 80:
            quality_issues.append("Low data completeness - many fields are empty")
        if validity_score < 90:
            quality_issues.append("Data validation issues detected")
        
        return {
            'completeness_score': round(completeness_score, 2),
            'validity_score': round(validity_score, 2),
            'quality_issues': quality_issues,
            'validation_errors_count': validation_error_count
        }
    
    def generate_api_results_summary(self, api_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API integration results summary"""
        if not api_results or not api_results.get('results'):
            return {
                'total_api_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'success_rate': 0,
                'api_errors': []
            }
        
        results = api_results['results']
        total_calls = results.get('total_processed', 0)
        successful_calls = results.get('total_successful', 0)
        failed_calls = results.get('total_failed', 0)
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Collect API errors
        api_errors = []
        for failed_call in results.get('failed', []):
            error_details = failed_call.get('error_details', {})
            api_errors.append({
                'customer_email': failed_call.get('customer_data', {}).get('email', 'Unknown'),
                'error_type': error_details.get('error', 'unknown'),
                'message': error_details.get('message', 'Unknown error')
            })
        
        return {
            'total_api_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'success_rate': round(success_rate, 2),
            'api_errors': api_errors[:10]  # Limit to first 10 errors
        }
    
    def generate_recommendations(self, processing_summary: Dict, data_quality: Dict, 
                               api_results: Dict, errors: List[Dict]) -> List[str]:
        """Generate recommendations based on processing results"""
        recommendations = []
        
        # Processing recommendations
        if processing_summary.get('success_rate', 0) < 80:
            recommendations.append("Consider reviewing and improving data quality before upload")
        
        # Data quality recommendations
        if data_quality.get('completeness_score', 0) < 80:
            recommendations.append("Improve data completeness by filling missing required fields")
        
        if data_quality.get('validity_score', 0) < 90:
            recommendations.append("Review data validation rules and fix invalid data formats")
        
        # API recommendations
        if api_results.get('success_rate', 0) < 90:
            recommendations.append("Check API connectivity and authentication settings")
        
        # Error-specific recommendations
        error_types = {}
        for error in errors:
            error_type = error.get('type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if error_types.get('parsing_error', 0) > 0:
            recommendations.append("Review CSV format and encoding issues")
        
        if error_types.get('missing_required_fields', 0) > 0:
            recommendations.append("Ensure all required fields are present in CSV header")
        
        return recommendations
    
    def generate_complete_report(self, 
                               processing_summary: Dict[str, Any],
                               data_quality: Dict[str, Any],
                               api_results: Dict[str, Any],
                               errors: List[Dict[str, Any]],
                               transformed_data: List[Dict],
                               processing_time: float) -> Dict[str, Any]:
        """Generate complete processing report"""
        
        # Generate all sections
        processing_section = self.generate_processing_summary(
            processing_summary.get('total_rows', 0),
            processing_summary.get('successful_rows', 0),
            processing_summary.get('failed_rows', 0),
            processing_time
        )
        
        quality_section = self.generate_data_quality_metrics(transformed_data, errors)
        api_section = self.generate_api_results_summary(api_results)
        recommendations = self.generate_recommendations(
            processing_section, quality_section, api_section, errors
        )
        
        return {
            'processing_summary': processing_section,
            'data_quality': quality_section,
            'api_results': api_section,
            'errors': {
                'total_errors': len(errors),
                'error_summary': self._summarize_errors(errors)
            },
            'recommendations': recommendations,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0',
                'system': 'CSV Upload System'
            }
        }
    
    def _summarize_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize errors by type"""
        error_summary = {}
        for error in errors:
            error_type = error.get('type', 'unknown')
            error_summary[error_type] = error_summary.get(error_type, 0) + 1
        return error_summary

def main(processing_summary: Dict[str, Any],
         data_quality: Dict[str, Any],
         api_results: Dict[str, Any],
         errors: List[Dict[str, Any]],
         transformed_data: List[Dict],
         processing_time: float) -> Dict[str, Any]:
    """
    Main function for Windmill integration
    
    Args:
        processing_summary: Summary of processing results
        data_quality: Data quality metrics
        api_results: API integration results
        errors: List of errors encountered
        transformed_data: Successfully transformed data
        processing_time: Total processing time in seconds
    
    Returns:
        Complete processing report
    """
    generator = ReportGenerator()
    return generator.generate_complete_report(
        processing_summary, data_quality, api_results, errors, transformed_data, processing_time
    )



