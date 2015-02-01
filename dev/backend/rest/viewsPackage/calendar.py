from rest.controllers.controllers import check_signed_in_request, is_valid_initDate_by_period


def calendar_get_by_period(request, period, initDate):
    check_signed_in_request(request, method='GET')
    if is_valid_initDate_by_period(period, initDate):
        pass
        # Match events for desired date.
        # Return (frontend does the rest).
