# calculator.py
from typing import List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from .models import Transaction, FinancialGoal, UserProfile
import math

class FinancialCalculator:
    """Калькулятор финансовых метрик"""
    
    @staticmethod
    def calculate_time_to_goal(
        goal: FinancialGoal,
        user_profile: UserProfile,
        monthly_savings: float = None
    ) -> Tuple[float, Dict[str, Any]]:
        if monthly_savings is None:
            monthly_savings = user_profile.monthly_income - user_profile.monthly_expenses
        
        amount_left = goal.amount_left
        
        if monthly_savings <= 0:
            return float('inf'), {
                "error": "Расходы превышают доходы",
                "monthly_savings": monthly_savings,
                "amount_left": amount_left
            }
        
        months_to_goal = amount_left / monthly_savings
        
        urgency_multiplier = {
            "urgent": 0.8,
            "short_term": 0.9,
            "medium_term": 1.0,
            "long_term": 1.1
        }
        
        priority_multiplier = {
            "critical": 0.7,
            "high": 0.85,
            "medium": 1.0,
            "low": 1.15
        }
        
        adjusted_months = months_to_goal
        if goal.priority in priority_multiplier:
            adjusted_months *= priority_multiplier[goal.priority]
        
        details = {
            "raw_months": months_to_goal,
            "adjusted_months": adjusted_months,
            "monthly_savings": monthly_savings,
            "amount_left": amount_left,
            "estimated_completion_date": (
                date.today() + timedelta(days=adjusted_months * 30)
            ).isoformat(),
            "priority_impact": f"{100 * (1 - priority_multiplier.get(goal.priority, 1)):.1f}%"
        }
        
        return max(0, adjusted_months), details
    
    @staticmethod
    def analyze_spending_patterns(
        transactions: List[Transaction],
        top_n: int = 5
    ) -> Dict[str, Any]:
        from collections import defaultdict
        
        category_expenses = defaultdict(float)
        category_counts = defaultdict(int)
        
        for t in transactions:
            if t.type == "expense":
                category_expenses[t.category] += t.amount
                category_counts[t.category] += 1
        
        sorted_categories = sorted(
            category_expenses.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_expenses = sum(category_expenses.values())
        
        top_categories = []
        for category, amount in sorted_categories[:top_n]:
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            top_categories.append({
                "category": category,
                "amount": amount,
                "percentage": percentage,
                "transaction_count": category_counts[category]
            })
        
        other_amount = sum(amount for _, amount in sorted_categories[top_n:])
        other_percentage = (other_amount / total_expenses * 100) if total_expenses > 0 else 0
        
        return {
            "total_expenses": total_expenses,
            "top_categories": top_categories,
            "other_categories": {
                "amount": other_amount,
                "percentage": other_percentage,
                "category_count": len(sorted_categories) - top_n
            },
            "category_count": len(sorted_categories),
            "average_transaction_size": total_expenses / len(transactions) if transactions else 0
        }
    
    @staticmethod
    def calculate_investment_growth(
        initial_amount: float,
        monthly_contribution: float,
        annual_return_rate: float,
        years: int
    ) -> Dict[str, float]:
        monthly_rate = annual_return_rate / 12 / 100
        
        future_value_initial = initial_amount * ((1 + monthly_rate) ** (years * 12))
        
        if monthly_rate > 0:
            future_value_annuity = monthly_contribution * (
                ((1 + monthly_rate) ** (years * 12) - 1) / monthly_rate
            )
        else:
            future_value_annuity = monthly_contribution * years * 12
        
        total_future_value = future_value_initial + future_value_annuity
        total_contributions = initial_amount + (monthly_contribution * years * 12)
        total_earnings = total_future_value - total_contributions
        
        return {
            "total_future_value": total_future_value,
            "total_contributions": total_contributions,
            "total_earnings": total_earnings,
            "annual_return_rate": annual_return_rate,
            "roi_percentage": (total_earnings / total_contributions * 100) if total_contributions > 0 else 0
        }
    
    @staticmethod
    def estimate_savings_from_cuts(
        current_monthly_expenses: float,
        categories_to_cut: Dict[str, float]
    ) -> Tuple[float, Dict[str, float]]:
        default_category_distribution = {
            "Еда": 0.25,
            "Транспорт": 0.15,
            "Развлечения": 0.20,
            "Коммуналка": 0.10,
            "Покупки": 0.20,
            "Прочее": 0.10
        }
        
        savings_by_category = {}
        total_savings = 0
        
        for category, reduction_percent in categories_to_cut.items():
            if category in default_category_distribution:
                category_expense = current_monthly_expenses * default_category_distribution[category]
                category_savings = category_expense * reduction_percent
                savings_by_category[category] = category_savings
                total_savings += category_savings
        
        return total_savings, savings_by_category