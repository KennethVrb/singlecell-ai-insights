from aws_cdk import Stack
from aws_cdk import aws_budgets as budgets


class BudgetStack(Stack):
    def __init__(self, scope, construct_id, email, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Monthly budget with email alerts
        budgets.CfnBudget(
            self,
            'MonthlyBudget',
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_type='COST',
                time_unit='MONTHLY',
                budget_limit=budgets.CfnBudget.SpendProperty(
                    amount=250,  # $250/month threshold
                    unit='USD',
                ),
                budget_name='sc-ai-insights-monthly-budget',
            ),
            notifications_with_subscribers=[
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        comparison_operator='GREATER_THAN',
                        notification_type='ACTUAL',
                        threshold=80,  # Alert at 80% ($200)
                        threshold_type='PERCENTAGE',
                    ),
                    subscribers=[
                        budgets.CfnBudget.SubscriberProperty(
                            subscription_type='EMAIL',
                            address=email,
                        )
                    ],
                ),
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        comparison_operator='GREATER_THAN',
                        notification_type='ACTUAL',
                        threshold=100,  # Alert at 100% ($250)
                        threshold_type='PERCENTAGE',
                    ),
                    subscribers=[
                        budgets.CfnBudget.SubscriberProperty(
                            subscription_type='EMAIL',
                            address=email,
                        )
                    ],
                ),
            ],
        )
