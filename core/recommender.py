# recommender.py
from typing import List, Dict, Any
import uuid
from .models import Recommendation, FinancialGoal, UserProfile
from .calculator import FinancialCalculator

class RecommendationEngine:
    """Движок рекомендаций"""
    
    def __init__(self):
        self.investment_strategies = {
            "conservative": {
                "name": "Консервативная стратегия",
                "description": "Вклады и гособлигации с низким риском",
                "annual_return": 6.5,
                "risk_level": 0.2,
                "min_horizon": 6
            },
            "balanced": {
                "name": "Сбалансированная стратегия",
                "description": "Смесь облигаций и ETF на акции",
                "annual_return": 10.2,
                "risk_level": 0.5,
                "min_horizon": 12
            },
            "aggressive": {
                "name": "Агрессивная стратегия",
                "description": "Акции роста и технологические ETF",
                "annual_return": 15.7,
                "risk_level": 0.8,
                "min_horizon": 24
            }
        }
    
    def generate_recommendations(
        self,
        goal: FinancialGoal,
        user_profile: UserProfile,
        spending_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        recommendations = []
        
        spending_recs = self._generate_spending_recommendations(
            goal, user_profile, spending_analysis
        )
        recommendations.extend(spending_recs)
        
        investment_recs = self._generate_investment_recommendations(
            goal, user_profile
        )
        recommendations.extend(investment_recs)
        
        income_recs = self._generate_income_recommendations(goal, user_profile)
        recommendations.extend(income_recs)
        
        recommendations.sort(key=lambda x: x.estimated_impact, reverse=True)
        
        return recommendations
    
    def _generate_spending_recommendations(
        self,
        goal: FinancialGoal,
        user_profile: UserProfile,
        spending_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        recs = []
        
        top_categories = spending_analysis.get("top_categories", [])
        
        for category in top_categories[:3]:
            cat_name = category["category"]
            cat_amount = category["amount"]
            
            reduction_potential = self._get_reduction_potential(cat_name)
            
            if reduction_potential > 0:
                estimated_savings = cat_amount * reduction_potential
                
                rec = Recommendation(
                    id=str(uuid.uuid4()),
                    title=f"Сократите расходы на '{cat_name}'",
                    description=(
                        f"Сократите расходы на {cat_name} на {reduction_potential*100:.0f}%. "
                        f"Вы тратите {cat_amount:.0f} руб/мес в этой категории."
                    ),
                    category="spending_cut",
                    estimated_impact=estimated_savings,
                    confidence=0.7,
                    actions=[
                        {
                            "action": "reduce_spending",
                            "category": cat_name,
                            "target_percentage": reduction_potential,
                            "current_amount": cat_amount,
                            "potential_savings": estimated_savings
                        }
                    ]
                )
                recs.append(rec)
        
        return recs
    
    def _generate_investment_recommendations(
        self,
        goal: FinancialGoal,
        user_profile: UserProfile
    ) -> List[Recommendation]:
        recs = []
        
        goal_horizon_months, _ = FinancialCalculator.calculate_time_to_goal(
            goal, user_profile
        )
        
        if goal_horizon_months >= 6:
            strategy_key = self._select_investment_strategy(
                user_profile.risk_tolerance,
                goal_horizon_months
            )
            
            if strategy_key:
                strategy = self.investment_strategies[strategy_key]
                
                monthly_investment = (user_profile.monthly_income - user_profile.monthly_expenses) * 0.2
                
                if monthly_investment > 0:
                    investment_growth = FinancialCalculator.calculate_investment_growth(
                        initial_amount=0,
                        monthly_contribution=monthly_investment,
                        annual_return_rate=strategy["annual_return"],
                        years=goal_horizon_months / 12
                    )
                    
                    rec = Recommendation(
                        id=str(uuid.uuid4()),
                        title=f"Инвестиционная стратегия: {strategy['name']}",
                        description=(
                            f"{strategy['description']}. "
                            f"Ожидаемая доходность: {strategy['annual_return']}% годовых. "
                            f"При инвестировании {monthly_investment:.0f} руб/мес вы можете заработать "
                            f"{investment_growth['total_earnings']:.0f} руб за {goal_horizon_months:.0f} месяцев."
                        ),
                        category="investment",
                        estimated_impact=investment_growth["total_earnings"] / goal_horizon_months,
                        confidence=0.6,
                        actions=[
                            {
                                "action": "start_investing",
                                "strategy": strategy_key,
                                "monthly_amount": monthly_investment,
                                "expected_annual_return": strategy["annual_return"],
                                "risk_level": strategy["risk_level"],
                                "estimated_total_earnings": investment_growth["total_earnings"]
                            }
                        ]
                    )
                    recs.append(rec)
        
        return recs
    
    def _generate_income_recommendations(
        self,
        goal: FinancialGoal,
        user_profile: UserProfile
    ) -> List[Recommendation]:
        recs = []
        
        if user_profile.monthly_income < 100000:
            rec = Recommendation(
                id=str(uuid.uuid4()),
                title="Рассмотрите дополнительные источники дохода",
                description=(
                    "Подработка или фриланс могут значительно ускорить достижение цели. "
                    "Даже 10-20 тыс. руб/мес дадут существенный эффект."
                ),
                category="income_increase",
                estimated_impact=15000,
                confidence=0.5,
                actions=[
                    {
                        "action": "explore_side_income",
                        "suggestions": [
                            "Фриланс по вашей основной специальности",
                            "Консультирование",
                            "Удаленная подработка"
                        ],
                        "potential_income_range": "10000-30000 руб/мес"
                    }
                ]
            )
            recs.append(rec)
        
        return recs
    
    def _get_reduction_potential(self, category: str) -> float:
        reduction_potentials = {
            "Развлечения": 0.3,
            "Рестораны/Кафе": 0.4,
            "Одежда": 0.25,
            "Подарки": 0.2,
            "Такси": 0.5,
            "default": 0.15
        }
        
        return reduction_potentials.get(category, reduction_potentials["default"])
    
    def _select_investment_strategy(
        self,
        risk_tolerance: float,
        horizon_months: int
    ) -> str:
        if horizon_months < 6:
            return None
        elif horizon_months < 12:
            return "conservative"
        elif horizon_months < 24:
            if risk_tolerance < 0.3:
                return "conservative"
            elif risk_tolerance < 0.7:
                return "balanced"
            else:
                return "aggressive"
        else:
            if risk_tolerance < 0.4:
                return "balanced"
            else:
                return "aggressive"
    
    def calculate_combined_impact(
        self,
        goal: FinancialGoal,
        user_profile: UserProfile,
        selected_recommendations: List[Recommendation]
    ) -> Dict[str, Any]:
        total_monthly_impact = 0
        new_monthly_savings = (
            user_profile.monthly_income - user_profile.monthly_expenses
        )
        
        for rec in selected_recommendations:
            total_monthly_impact += rec.estimated_impact
            
            if rec.category == "spending_cut":
                new_monthly_savings += rec.estimated_impact
            elif rec.category == "income_increase":
                new_monthly_savings += rec.estimated_impact
        
        new_months, details = FinancialCalculator.calculate_time_to_goal(
            goal, user_profile, new_monthly_savings
        )
        
        original_months, _ = FinancialCalculator.calculate_time_to_goal(
            goal, user_profile
        )
        
        time_reduction = original_months - new_months if original_months != float('inf') else 0
        time_reduction_percent = (
            (time_reduction / original_months * 100) if original_months > 0 else 0
        )
        
        return {
            "original_months": original_months,
            "new_months": new_months,
            "time_reduction_months": time_reduction,
            "time_reduction_percent": time_reduction_percent,
            "total_monthly_impact": total_monthly_impact,
            "new_monthly_savings": new_monthly_savings,
            "estimated_completion_date": details.get("estimated_completion_date"),
            "impact_by_category": {
                rec.category: rec.estimated_impact for rec in selected_recommendations
            }
        }