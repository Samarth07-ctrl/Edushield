"""
Explainable AI Module — EduShield AI
Uses SHAP (SHapley Additive exPlanations) to explain
why the readiness model predicted a certain placement probability.
"""

import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Try importing SHAP — fall back gracefully if not installed
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not installed. Explainability will use weight-based fallback.")

from readiness_model import get_model, FEATURES, FEATURE_LABELS, generate_synthetic_placement_data


def explain_prediction(student_profile: Dict[str, float]) -> Dict[str, Any]:
    """
    Explain the readiness model's prediction using SHAP values.
    
    If SHAP is unavailable, falls back to coefficient-based explanation.
    
    Args:
        student_profile: Student's feature values
    
    Returns:
        {
            "positive_factors": [...],
            "negative_factors": [...],
            "shap_values": {...},
            "base_value": float,
            "prediction": float
        }
    """
    model = get_model()
    
    if not model.is_trained:
        model._train_on_synthetic()
    
    # Build feature vector
    feature_vector = np.array([[
        student_profile.get(f, 0) for f in FEATURES
    ]])
    
    feature_scaled = model.scaler.transform(feature_vector)
    
    if SHAP_AVAILABLE:
        return _explain_with_shap(model, feature_scaled, student_profile)
    else:
        return _explain_with_weights(model, feature_scaled, student_profile)


def _explain_with_shap(model, feature_scaled, student_profile):
    """Use SHAP library for proper Shapley value explanations"""
    try:
        # Create background dataset for SHAP
        X_background, _ = generate_synthetic_placement_data(100, seed=99)
        X_bg_scaled = model.scaler.transform(X_background)
        
        # Create SHAP explainer
        explainer = shap.LinearExplainer(model.model, X_bg_scaled)
        
        # Get SHAP values for this prediction
        shap_values = explainer.shap_values(feature_scaled)
        
        # shap_values shape depends on version — handle both
        if isinstance(shap_values, list):
            sv = shap_values[1][0]  # class 1 (placed)
        elif len(shap_values.shape) == 3:
            sv = shap_values[0, :, 1]
        else:
            sv = shap_values[0]
        
        base_value = float(explainer.expected_value)
        if isinstance(base_value, np.ndarray):
            base_value = float(base_value[1]) if len(base_value) > 1 else float(base_value[0])
        
        return _format_explanation(sv, student_profile, base_value)
    
    except Exception as e:
        logger.warning(f"SHAP explanation failed, falling back to weights: {e}")
        return _explain_with_weights(model, feature_scaled, student_profile)


def _explain_with_weights(model, feature_scaled, student_profile):
    """Fallback: use model coefficients * scaled features as approximate explanation"""
    coefficients = model.model.coef_[0]
    contributions = coefficients * feature_scaled[0]
    base_value = float(model.model.intercept_[0])
    
    return _format_explanation(contributions, student_profile, base_value)


def _format_explanation(contributions, student_profile, base_value):
    """Format SHAP/weight contributions into positive and negative factors"""
    positive_factors = []
    negative_factors = []
    shap_dict = {}
    
    for i, feat in enumerate(FEATURES):
        impact = float(contributions[i])
        label = FEATURE_LABELS.get(feat, feat)
        value = student_profile.get(feat, 0)
        
        shap_dict[feat] = {
            "impact": round(impact, 4),
            "value": value,
            "label": label
        }
        
        entry = {
            "feature": feat,
            "label": label,
            "impact": round(impact, 4),
            "value": value
        }
        
        if impact >= 0:
            positive_factors.append(entry)
        else:
            negative_factors.append(entry)
    
    # Sort by absolute impact (most important first)
    positive_factors.sort(key=lambda x: -x["impact"])
    negative_factors.sort(key=lambda x: x["impact"])
    
    # Get readiness prediction for context
    model = get_model()
    feature_vector = np.array([[student_profile.get(f, 0) for f in FEATURES]])
    feature_scaled = model.scaler.transform(feature_vector)
    probability = float(model.model.predict_proba(feature_scaled)[0][1])
    
    return {
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "shap_values": shap_dict,
        "base_value": round(base_value, 4),
        "prediction_probability": round(probability, 4),
        "readiness_score": round(probability * 100, 1),
        "method": "shap" if SHAP_AVAILABLE else "coefficient_based",
        "explanation_summary": _generate_summary(positive_factors, negative_factors, probability)
    }


def _generate_summary(positive, negative, probability):
    """Generate a human-readable summary of the explanation"""
    score = round(probability * 100, 1)
    
    lines = [f"Your placement readiness score is {score}%."]
    
    if positive:
        top_pos = positive[0]
        lines.append(
            f"Your strongest factor is {top_pos['label']} "
            f"(value: {top_pos['value']}), which boosts your score the most."
        )
    
    if negative:
        top_neg = negative[0]
        lines.append(
            f"Your biggest area for improvement is {top_neg['label']} "
            f"(value: {top_neg['value']}), which is pulling your score down."
        )
    
    if score >= 70:
        lines.append("You are in a strong position for placement.")
    elif score >= 40:
        lines.append("With focused preparation, you can significantly improve your chances.")
    else:
        lines.append("Consider strengthening your fundamentals and gaining practical experience.")
    
    return " ".join(lines)
