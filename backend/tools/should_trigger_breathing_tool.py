from datetime import datetime
from typing import Optional, Dict


async def should_trigger_breathing_tool(
    emotion: str,
    heart_rate: Optional[float],
    hrv: Optional[float],
    context: Optional[str] = "rest",  # rest, sleep, exercise
    user_baseline_hrv: Optional[float] = None,
    population_hrv_average: float = 50.0,
    weather: Optional[Dict[str, float]] = None,
    timestamp: Optional[datetime] = None
) -> Dict:
    """
    Analyze user emotion, physiological data, and context to determine
    whether a breathing or mindfulness reminder should be recommended.

    :param emotion: User's current emotional state (e.g., anxious, calm, sad)
    :param heart_rate: Current heart rate in BPM
    :param hrv: Heart rate variability in ms
    :param context: Current user state: rest, sleep, or exercise
    :param user_baseline_hrv: Average HRV value for this specific user
    :param population_hrv_average: General average HRV for population
    :param weather: Weather info dict with temperature_c, humidity, etc.
    :param timestamp: Optional timestamp of data collection
    :return: Dict containing recommendation and reasoning
    """
    reasons = []
    should_recommend = False

    # Emotion signal
    if emotion.lower() in ["anxious", "angry", "sad"]:
        reasons.append(f"Detected negative emotion: {emotion}")
        should_recommend = True

    # HRV check against user baseline and population average
    if hrv is not None:
        if user_baseline_hrv and hrv < user_baseline_hrv * 0.8:
            reasons.append(
                f"HRV ({hrv:.1f}) is lower than personal baseline ({user_baseline_hrv})")
            should_recommend = True
        elif hrv < population_hrv_average * 0.7:
            reasons.append(
                f"HRV ({hrv:.1f}) is significantly lower than population average ({population_hrv_average})")
            should_recommend = True

    # Heart rate based on context
    if heart_rate is not None:
        if context == "sleep" and heart_rate > 80:
            reasons.append(
                f"Heart rate during sleep is elevated: {heart_rate} BPM")
            should_recommend = True
        elif context == "rest" and heart_rate > 95:
            reasons.append(f"Heart rate at rest is high: {heart_rate} BPM")
            should_recommend = True
        elif context == "exercise" and heart_rate < 90:
            reasons.append(
                f"Heart rate during exercise seems unusually low: {heart_rate} BPM")
            should_recommend = True

    # Weather-based influence
    if weather:
        temp = weather.get("temperature_c")
        humidity = weather.get("humidity")
        if temp and humidity:
            if temp > 30 and humidity > 70:
                reasons.append(
                    f"Hot and humid weather ({temp}°C, {humidity}%) may impact mood")
                should_recommend = True

    return {
        "recommend_breathing": should_recommend,
        "reason": "; ".join(reasons) if reasons else "No strong indicators for stress detected",
        "suggestion": "Consider a 3-minute breathing or mindfulness session" if should_recommend else "No action needed",
        "context": context,
        "timestamp": timestamp.isoformat() if timestamp else datetime.now().isoformat()
    }
