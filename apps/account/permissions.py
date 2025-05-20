# Define permissions for different roles
ROLE_PERMISSIONS = {
    "chef": ["can_access_report_notebook", "can_access_close_shift_waitress", ],
    "administrator": ["can_access_all"],
    "waitress": ["can_access_waitress_page"],
    # Add more roles and permissions as needed
}

# Define specific views permissions
VIEW_PERMISSIONS = {
    # CHEF PERMISSIONS
    "ReportNoteBook": ["chef"],
    "RequestToCloseShiftWaitress": ["chef"],
    "RequestShiftDetailView": ["chef"],
    "EndRequestShiftDetailView": ["chef"],
    "DebtsWaitressByMonth": ["chef"],
    "DebtsByMonthDetailView": ["chef"],
    "DebtPaidByMonth": ["chef"],
    "SettingsProgramView": ["chef"],
    "InComeView": ["chef"],
    # WAITRESS
    "BreadPage": ["chef", "waitress"],
    "EditBreadMainPageView": ["chef", "waitress"],
    "DeleteBreadMainPageView": ["chef", "waitress"],
    "EditBreadComingView": ["chef", "waitress"],
    "WaitressBreadDeleteView": ["chef", "waitress"],
    "StartShiftWaitress": ["chef", "administrator", "employee", "waitress"],
    "WaitressPageView": ["waitress"],
    "StartLateUserShiftWaitress": ["employee", "waitress"],
    "DesksSimpleView": ["waitress"],
    "DesksView": ["waitress"],
    "NewOrderView": ["waitress"],
    "EditOrderWaitress": ["waitress"],
    "KitchenWaitressView": ["waitress"],
    "BillWaitressView": ["waitress"],
    "BillWaitressDetailView": ["waitress"],
    "EndOrder": ["waitress"],
    "TakeAwayFoodView": ["waitress"],
    "NewOrderTakeAwayFood": ["waitress"],
    "BillTakeAwayFoodView": ["waitress"],
    "ListOfItemsWaitressView": ["waitress"],
    "BalanceFromCardView": ["waitress"],
    "EditOrderWaitressTakeAwayView": ["waitress"],
    "ConsumptionsWaitressHistoryView": ["waitress", "chef"],
    "ConsumptionsWaitressView": ["waitress"],
    "EndShiftWaitress": ["waitress"],
    "ProfilePageView": ["waitress", "chef", "administrator", "employee"],

    # CHEF ADMINISTRATOR
    "HomePageView": ["chef", "administrator", "employee", "samsishnik"],
    "SettingsListView": ["chef", "administrator"],
    "WantToStartShift": ["chef", "administrator", "employee"],
    "ConfirmShiftStart": ["chef", "administrator", "employee"],
    "OrdersInKitchenView": ["chef", "administrator", "employee"],
    "ControlKitchenOrders": ["chef", "administrator", "employee"],
    "DeleteOrderView": ["chef", "administrator", "employee", "samsishnik"],
    "ControlDeletedOrderView": ["chef", "administrator"],
    "HistoryBillIsPaidView": ["chef", "administrator"],
    "RecoveryDeletedMealView": ["chef", "administrator", "employee"],
    "OrdersTea": ["chef", "administrator", "employee"],
    "ListOfNominationOrderView": ["chef", "administrator", "employee"],
    "MealListView": ["chef", "administrator", "employee"],
    "MealSearchView": ["chef", "administrator", "employee"],
    "AddMealView": ["chef", "administrator"],
    "EditMealsView": ["chef", "administrator"],
    "CommentsInMealView": ["chef", "administrator"],
    "EditCommentsMealsInMenu": ["chef", "administrator"],
    "StopListView": ["chef", "administrator", "employee"],
    "GroupStopListView": ["chef", "administrator", "employee"],
    "AddGroupNameToStopListView": ["chef", "administrator", "employee"],
    "AddGroupItemToStopListView": ["chef", "administrator", "employee"],
    "MenuView": ["chef", "administrator", "employee", "waitress"],
    "QuantityOfMealADay": ["chef", "administrator", "samsishnik"],
    "RatingMealView": ["chef", "administrator"],
    "MealInStockView": ["chef", "administrator", "employee"],
    "MeatOrderPageView": ["chef", "administrator", "employee"],
    "EditOrderMeatView": ["chef", "administrator", "employee"],

    # SAMSA KEBAB
    "OrdersSamsaKebabView": ["chef", "administrator", "employee", "samsishnik"],
    "ControlSamsaKebabOrders": ["chef", "administrator", "samsishnik"],
    "SamsaReportAddView": ["chef", "administrator", "samsishnik"],
    "SamsaSettingsView": ["chef", "administrator", "samsishnik"],
    "EditSamsaConsumption": ["chef", "administrator", "samsishnik"],


    "ButcherMainView": ["chef", "butcher"],
    "ButcherMeatOrdersView": ["chef", "butcher"],
    "HistoryButcherMeatOrdersView": ["chef", "butcher"],
    "UnPaidMeatOrdersView": ["chef", "butcher"],

    # CHEF
    "SaleDayView": ["chef"],
    "MealReportList": ["chef"],
    "ProductPriceView": ["chef"],
    "MealRecipesView": ["chef"],
    "NotEndedReportView": ["chef"],
    "ReportByHourView": ["chef"],

    # Add more views and the allowed roles for each
}
