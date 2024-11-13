from rest_framework.generics import CreateAPIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from lipanampesa.models import MpesaTransaction
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.views import View
from django.http import HttpResponse, JsonResponse
import pytz
from datetime import datetime
from django.utils import timezone
import json
from rest_framework.permissions import AllowAny


class MpesaExpressCallback(CreateAPIView):
    def create(self, request):
        print("This is the request data",request.data)
        CheckoutRequestID = request.data["Body"]["stkCallback"]["CheckoutRequestID"]
        MerchantRequestID = request.data["Body"]["stkCallback"]["MerchantRequestID"]
        ResultCode = request.data["Body"]["stkCallback"]["ResultCode"]
        ResultDesc = request.data["Body"]["stkCallback"]["ResultDesc"]

        items = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"] 
        for item in items:
            try:
                if item["Name"] == "Amount":
                    Amount = item["Value"]
                elif item["Name"] == "MpesaReceiptNumber":
                    MpesaReceiptNumber = item["Value"]
                elif item["Name"] == "PhoneNumber":
                    PhoneNumber = item["Value"]
                elif item["Name"] == "TransactionDate":
                    TransactionDate = item["Value"]
            except KeyError:
                resultcode = request.data["Body"]["stkCallback"]["ResultCode"]
                if resultcode == 1032:
                    message = "You cancelled the MPESA request."                
                elif resultcode == 2001:
                    message = "The PIN you entered was incorrect."                
                elif resultcode == 1037:
                    message = "The MPESA request timed out."
                elif resultcode == 1:
                    message = "Insufficient funds"                
                else:
                    print("Everuthing seems to be fine")
                print("This is the error message : ",message)
            
        str_transaction_date = str(TransactionDate)
        transaction_datetime = datetime.strptime(str_transaction_date, "%Y%m%d%H%M%S")
        aware_transaction_datetime = pytz.utc.localize(transaction_datetime)

        print(aware_transaction_datetime, "this should be datetime")
        print(PhoneNumber, "this should be an phone_number")
        print(CheckoutRequestID, "this should be an Checkout ID")
        print(MpesaReceiptNumber, "this should be an Receipt Number")
        print(Amount, "this should be the Amount")
        print(MerchantRequestID, "this should be MerchantRequestID")
        print(ResultCode, "this should be result code")
        print(ResultDesc, "this should be result desc")

        mpesa_trans = MpesaTransaction.objects.create(

                TransactionDate = aware_transaction_datetime,
                Amount = Amount,
                PhoneNumber = PhoneNumber,
                MpesaReceiptNumber = MpesaReceiptNumber,
                CheckoutRequestID = CheckoutRequestID,
                MerchantRequestID = MerchantRequestID,
                ResultCode = ResultCode,
                ResultDesc = ResultDesc,
       
        )
        mpesa_trans.save()
        return Response({"OurResultDesc": "YEEY!!! It worked!"})
