from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
import requests
import calendar
import datetime
import pickle
import ibm_boto3
from ibm_botocore.client import Config
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson_machine_learning import APIClient
import subprocess
import sys
import types

# Models
from .models import Registration, LetterOfCredit
from .utils import get_deployment_id, save_deployment_id

# Watsonx API Key
api_key = 'D8b1DDcl2_RJmRPOA-TuKMEswta0F9PY50y9gzj1vCD-'

def deployable_callable():

    # Check if a deployment ID already exists
    deployment_id = get_deployment_id()
    if deployment_id:
        print("Using existing Deployment ID:", deployment_id)
        return deployment_id

    def score(payload):
        import ibm_boto3
        from ibm_botocore.client import Config
        import pickle
        import calendar
        import datetime
        import types
        class Utils:
            def __init__(self):
                pass

            def months_between_january(self, start_month):
                months = list(calendar.month_name)
                january_index = 1
                target_index = months.index(start_month)
                months_difference = target_index - january_index
                return months_difference + 1

            def generate_month_year_tuples(self, start_month, start_year):
                months = list(calendar.month_name)
                start_index = months.index(start_month)
                result = []
                for i in range(12):
                    month_index = (start_index + i) % 12 + 1
                    year = start_year + (start_index + i) // 12
                    result.append((months[month_index], year))
                return result

            def prepare_response(self, start_month, fc_results):
                lc_projections = []
                start_year = datetime.datetime.now().year
                months_years = self.generate_month_year_tuples(start_month, start_year)
                for fc, my in zip(fc_results, months_years):
                    lc_projections.append({
                        "month": my[0],
                        "year": my[1],
                        "predicted_lcs": fc
                    })
                return lc_projections

        # IBM Cloud Object Storage details
        bucket = 'letterofcreditngsbucket'
        object_key = 'arima_model.pkl'
        cos_client = ibm_boto3.client(
            service_name='s3',
            ibm_api_key_id="D8b1DDcl2_RJmRPOA-TuKMEswta0F9PY50y9gzj1vCD-",
            ibm_auth_endpoint="https://iam.cloud.ibm.com/oidc/token",
            config=Config(signature_version='oauth'),
            endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
        )

        # Retrieve the model from IBM Cloud Object Storage
        body = cos_client.get_object(Bucket=bucket, Key=object_key)['Body']
        if not hasattr(body, "__iter__"):
            body.__iter__ = types.MethodType(lambda self: iter(self._raw_stream), body)

        # Load the model
        arima_model = pickle.load(body)

        start_month = payload['input_data'][0]['values'][0][0]
        fc_period = 12

        utl = Utils()
        lapse_months = utl.months_between_january(start_month)
        target_months = lapse_months + fc_period
        forecast = arima_model.forecast(steps=target_months)

        fc_results = [round(l) for l in list(forecast.tolist())]
        rqd_results = fc_results[lapse_months:]
        lc_projections = utl.prepare_response(start_month, rqd_results)

        return {"predictions": lc_projections}

    wml_credentials = {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": api_key
    }
    client = APIClient(wml_credentials)
    client.set.default_space("cd4784f3-981f-4219-98df-b52feb340fc0")

    model_props = {
        client.repository.FunctionMetaNames.NAME: "LC ARIMA Model Function",
        client.repository.FunctionMetaNames.SOFTWARE_SPEC_UID: client.software_specifications.get_id_by_name("runtime-24.1-py3.11")
    }

    published_model = client.repository.store_function(meta_props=model_props, function=score)

    deployment_props = {
        client.deployments.ConfigurationMetaNames.NAME: "LC ARIMA Function Deployment",
        client.deployments.ConfigurationMetaNames.ONLINE: {}
    }

    deployment = client.deployments.create(published_model['metadata']['id'], meta_props=deployment_props)
    deployment_id = deployment['metadata']['id']
    print("Model deployed successfully with Deployment ID:", deployment_id)

    # Save the new deployment ID
    save_deployment_id(deployment_id)
    return deployment_id

deployment_id = deployable_callable()

authenticator = IAMAuthenticator(api_key)
access_token = authenticator.token_manager.get_token()
headers = {'Authorization': 'Bearer ' + access_token}

def predict_lc(request):
    if request.method == 'POST':
        start_month = request.POST.get('current_month')

        if not start_month:
            return render(request, 'myapp/predict_lc.html', {
                'results': [],
                'error': 'Start month is required.'
            })

        fc_period = 12
        endpoint_url = f'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/{deployment_id}/predictions?version=2021-05-01'
        input_payload = {
            "input_data": [
                {
                    "fields": ["month"],
                    "values": [[start_month]]
                }
            ]
        }

        response = requests.post(endpoint_url, json=input_payload, headers=headers)

        if response.status_code != 200:
            print("Error:", response.status_code)
            print("Response Content:", response.content)
            return render(request, 'myapp/predict_lc.html', {
                'results': [],
                'error': 'Error occurred during prediction.'
            })

        lc_projections = response.json().get('predictions', [])
        return render(request, 'myapp/predict_lc.html', {
            'lc_projections': lc_projections,
            'error': None
        })

    return render(request, 'myapp/predict_lc.html')

def loginForm(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Registration.objects.get(email=email)
            if user.password == password:
                return redirect('dashboardPage')
            else:
                messages.error(request, 'Invalid email or password.')
        except Registration.DoesNotExist:
            messages.error(request, 'User does not exist. Please register first.')
            return redirect('registrationForm')

    return render(request, 'myapp/loginForm.html')

def registrationForm(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        bio = request.POST.get('bio')

        if not username or not email or not password:
            messages.error(request, 'Username, Email, and Password are required.')
            return render(request, 'myapp/registrationForm.html')

        if Registration.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'myapp/registrationForm.html')
        if Registration.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'myapp/registrationForm.html')

        user = Registration(username=username, email=email, phone=phone, password=password, bio=bio)
        user.save()
        return redirect('loginForm')
    else:
        return render(request, 'myapp/registrationForm.html')

def dashboardPage(request):
    return render(request, 'myapp/dashboardPage.html')

def add_lc(request):
    if request.method == 'POST':
        lc_number = request.POST.get('lc_number')
        applicant_name = request.POST.get('applicant_name')
        beneficiary_name = request.POST.get('beneficiary_name')
        issuing_bank = request.POST.get('issuing_bank')
        advising_bank = request.POST.get('advising_bank')
        negotiating_bank = request.POST.get('negotiating_bank')
        confirming_bank = request.POST.get('confirming_bank')
        lc_amount = request.POST.get('lc_amount')
        currency = request.POST.get('currency')
        issue_date = request.POST.get('issue_date')
        expiry_date = request.POST.get('expiry_date')
        status = request.POST.get('status')

        lc = LetterOfCredit(
            lc_number=lc_number,
            applicant_name=applicant_name,
            beneficiary_name=beneficiary_name,
            issuing_bank=issuing_bank,
            advising_bank=advising_bank,
            negotiating_bank=negotiating_bank,
            confirming_bank=confirming_bank,
            lc_amount=lc_amount,
            currency=currency,
            issue_date=issue_date,
            expiry_date=expiry_date,
            status=status
        )
        lc.save()
        messages.success(request, 'Letter of Credit created successfully!')
        return redirect('dashboardPage')

    return render(request, 'myapp/add_lc.html')

def view_lc(request):
    lcs = LetterOfCredit.objects.all()
    return render(request, 'myapp/view_lc.html', {'lcs': lcs})

class LCForm(forms.ModelForm):
    class Meta:
        model = LetterOfCredit
        fields = [
            'lc_number', 'applicant_name', 'beneficiary_name', 'issuing_bank',
            'advising_bank', 'negotiating_bank', 'confirming_bank',
            'lc_amount', 'currency', 'issue_date', 'expiry_date', 'status'
        ]

def edit_lc(request, lc_id):
    lc = get_object_or_404(LetterOfCredit, id=lc_id)
    if request.method == 'POST':
        form = LCForm(request.POST, instance=lc)
        if form.is_valid():
            form.save()
            return redirect('view_lc')
    else:
        form = LCForm(instance=lc)
    return render(request, 'myapp/edit_lc.html', {'form': form})

def delete_lc(request, lc_id):
    lc = get_object_or_404(LetterOfCredit, id=lc_id)
    if request.method == 'POST':
        lc.delete()
        return redirect('view_lc')
    return render(request, 'myapp/delete_lc.html', {'lc': lc})

def approve_lc(request, lc_id):
    lc = get_object_or_404(LetterOfCredit, id=lc_id)
    if request.method == 'POST':
        approval_status = request.POST.get('approval_status')
        if approval_status == 'approved':
            lc.status = 'Approved'
        else:
            lc.status = 'Rejected'
        lc.save()
        return HttpResponseRedirect(reverse('view_lc'))
    return render(request, 'myapp/approve_lc.html', {'lc': lc})

def index(request):
    return render(request, 'myapp/welcomePage.html')

def navbar(request):
    return render(request, 'myapp/navbar.html')

def sidebar(request):
    return render(request, 'myapp/sidebar.html')
