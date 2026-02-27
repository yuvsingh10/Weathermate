"""Detailed air quality information and health recommendations."""

from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class AirQualityDetails:
    """Provide detailed AQI information and health recommendations."""
    
    # AQI to health level mapping
    AQI_LEVELS = {
        1: {"label": "Good", "color": "🟢", "advice": "Air quality is satisfactory"},
        2: {"label": "Fair", "color": "🟡", "advice": "Acceptable air quality"},
        3: {"label": "Moderate", "color": "🟠", "advice": "Sensitive groups may experience issues"},
        4: {"label": "Poor", "color": "🔴", "advice": "Everyone may experience health effects"},
        5: {"label": "Very Poor", "color": "⚫", "advice": "Health alert: risk of serious effects"},
    }
    
    POLLUTANTS = {
        "PM2.5": "Particulate Matter 2.5µm (Fine particles)",
        "PM10": "Particulate Matter 10µm (Coarse particles)",
        "O3": "Ozone",
        "NO2": "Nitrogen Dioxide",
        "SO2": "Sulfur Dioxide",
        "CO": "Carbon Monoxide"
    }
    
    @staticmethod
    def get_aqi_info(aqi_level: int) -> Dict[str, str]:
        """Get information about an AQI level.
        
        Args:
            aqi_level: AQI level (1-5)
            
        Returns:
            Dictionary with label, emoji, and health advice
        """
        return AirQualityDetails.AQI_LEVELS.get(
            aqi_level,
            {"label": "Unknown", "color": "❓", "advice": ""}
        )
    
    @staticmethod
    def get_health_recommendations(aqi_level: int) -> str:
        """Get health recommendations based on AQI level.
        
        Args:
            aqi_level: AQI level (1-5)
            
        Returns:
            Health recommendations text
        """
        level_info = AirQualityDetails.get_aqi_info(aqi_level)
        
        recommendations = {
            1: (
                "✅ Air quality is good\n"
                "• Enjoy outdoor activities\n"
                "• No health concerns"
            ),
            2: (
                "✅ Air quality is acceptable\n"
                "• Outdoor activities are fine\n"
                "• Sensitive groups: mild effects possible"
            ),
            3: (
                "⚠️ Moderate air quality\n"
                "• Sensitive groups (kids, elderly): limit outdoor activities\n"
                "• Consider wearing masks if sensitive"
            ),
            4: (
                "🔴 Poor air quality\n"
                "• Everyone: reduce prolonged outdoor activities\n"
                "• Use air purifiers indoors\n"
                "• Wear N95 masks if going outside"
            ),
            5: (
                "🚨 Very poor air quality - HEALTH ALERT\n"
                "• STAY INDOORS if possible\n"
                "• Keep windows closed\n"
                "• Use HEPA air purifiers\n"
                "• Wear N95/P100 masks if outdoors\n"
                "• Check with health provider if symptoms arise"
            )
        }
        
        return recommendations.get(aqi_level, "Level unknown")
    
    @staticmethod
    def get_affected_groups(aqi_level: int) -> str:
        """Get info about which groups are affected.
        
        Args:
            aqi_level: AQI level (1-5)
            
        Returns:
            Text describing affected populations
        """
        groups = {
            1: "No sensitive groups affected",
            2: "Unusually sensitive people may be affected",
            3: (
                "Sensitive groups at risk:\n"
                "• Children (under 15)\n"
                "• Elderly (over 65)\n"
                "• People with respiratory/heart disease"
            ),
            4: (
                "Everyone at risk:\n"
                "• Members of sensitive groups more vulnerable\n"
                "• General population may experience symptoms"
            ),
            5: (
                "SEVERE - Everyone at high risk:\n"
                "• Serious health effects expected\n"
                "• Emergency services activated\n"
                "• Vulnerable populations in critical danger"
            )
        }
        
        return groups.get(aqi_level, "Unknown risk level")
    
    @staticmethod
    def get_precautions(aqi_level: int) -> str:
        """Get specific precautions to take.
        
        Args:
            aqi_level: AQI level (1-5)
            
        Returns:
            Precautions text
        """
        precautions = {
            1: "• No precautions needed",
            2: "• Consider air quality if planning outdoor sports",
            3: (
                "• Reduce outdoor activities for sensitive groups\n"
                "• Keep medications handy\n"
                "• Monitor air quality updates"
            ),
            4: (
                "• Limit outdoor activities for everyone\n"
                "• Use masks (N95) if going out\n"
                "• Stay hydrated\n"
                "• Avoid strenuous exercise outdoors"
            ),
            5: (
                "• AVOID outdoor exposure\n"
                "• Keep indoors with closed windows\n"
                "• Use air purifier with HEPA filter\n"
                "• Wear N95/P100 mask if you must go out\n"
                "• Contact healthcare provider if symptoms appear"
            )
        }
        
        return precautions.get(aqi_level, "Precautions unknown")
    
    @staticmethod
    def get_detailed_report(aqi_level: int) -> str:
        """Generate a comprehensive AQI report.
        
        Args:
            aqi_level: AQI level (1-5)
            
        Returns:
            Detailed report text
        """
        info = AirQualityDetails.get_aqi_info(aqi_level)
        
        report = f"\n{'='*50}\n"
        report += f"AIR QUALITY REPORT\n"
        report += f"{'='*50}\n\n"
        report += f"Level: {info['color']} {info['label'].upper()}\n\n"
        
        report += "📋 SUMMARY:\n"
        report += f"{info['advice']}\n\n"
        
        report += "👥 AFFECTED GROUPS:\n"
        report += AirQualityDetails.get_affected_groups(aqi_level) + "\n\n"
        
        report += "💊 HEALTH RECOMMENDATIONS:\n"
        report += AirQualityDetails.get_health_recommendations(aqi_level) + "\n\n"
        
        report += "⚕️ PRECAUTIONS:\n"
        report += AirQualityDetails.get_precautions(aqi_level) + "\n\n"
        
        report += "🏭 MAIN POLLUTANTS:\n"
        report += "• PM2.5: Fine particulates (harmful)\n"
        report += "• PM10: Coarse particles\n"
        report += "• O3: Ground-level ozone\n"
        report += "• NO2: Nitrogen dioxide from vehicles\n\n"
        
        report += "💡 TIPS:\n"
        report += "• Check air quality daily\n"
        report += "• Use air quality apps for updates\n"
        report += "• Plan outdoor activities when AQI is low\n"
        report += "• Invest in a good air purifier\n"
        
        return report
