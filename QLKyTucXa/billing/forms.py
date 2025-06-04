from django import forms


class InvoiceInputForm(forms.Form):
    room_id = forms.IntegerField(widget=forms.HiddenInput)
    electricity_fee = forms.DecimalField(label="Electricity Fee", min_value=0, max_digits=10, decimal_places=2)
    water_fee = forms.DecimalField(label="Water Fee", max_digits=10, min_value=0, decimal_places=2)
    other_services_fee = forms.DecimalField(label="Other Services", max_digits=10, min_value=0, decimal_places=2,
                                            required=False,
                                            initial=0)
