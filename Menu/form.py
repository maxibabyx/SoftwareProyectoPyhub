# -*- coding: utf-8 -*-
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Permission
from Registro.models import ingrediente, perfil, proveedor, menu, item,contiene,posee
import datetime

'''
      Forma para crear y editar un menu
'''
class formMenu(forms.Form):

    nombreMenu = forms.CharField(widget=forms.TextInput(attrs={'type':'text' ,'class':'form-control' ,'id':'inputNombreMenu', 'placeholder':'Nombre Menu',}),label = "Nombre de Menu:")
    platos = forms.ModelMultipleChoiceField(item.objects.all(), required=True, widget=forms.CheckboxSelectMultiple(attrs={'type':"checkbox",}), label='Selecciona los objetos del menu')

    def __init__(self, menuId = None, *args, **kwargs):
        super(formMenu, self).__init__(*args, **kwargs)
        if menuId:
            self.fields['platos'].initial = [c.idItem.idItem for c in contiene.objects.filter(idMenu = menuId)]
            self.fields['nombreMenu'].initial = menu.objects.get(idMenu = menuId).nombre

    def save(self, menuId):
        actual = [x.idItem for x in contiene.objects.filter(idMenu = menuId)]
        remover = [x for x in actual if x not in self.cleaned_data['platos']]
        agregar = [x for x in self.cleaned_data['platos'] if x not in actual]
        menuObj = menu.objects.get(idMenu = menuId)
        menuObj.nombre = self.cleaned_data['nombreMenu']
        menuObj.save()
        for x in agregar:
            contiene.objects.create(idMenu = menuObj, idItem = x)
        for x in remover:
            contiene.objects.filter(idMenu = menuObj, idItem = x).delete()
        return None

    def create(self):
        return menu.objects.create(nombre = self.cleaned_data['nombreMenu']).idMenu

'''
     Forma para ingredientes
'''
class ingredienteForm(forms.ModelForm):
    
    class Meta:
        model = ingrediente
        exclude = ['idIngr']
    
    def __init__(self, *args, **kwargs):
        super(ingredienteForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'type':'text' ,'class':'form-control' ,'id':'inputIngrediente', 'placeholder':'Ingrediente'})
        self.fields['cantidad'].widget.attrs.update({'type':'number', 'class':'form-control', 'id':'inputNumber' ,'min':'0', 'data-bind':'value:replyNumber'})

'''
      Forma para platos
'''
class formPlato(forms.ModelForm):
    class Meta:
        model = item
        exclude = ['idItem','poseeRel']

    def __init__(self, *args, **kwargs):
        super(formPlato, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'type':'text' ,'class':'form-control' , 'placeholder':'Plato'})
        self.fields['tipo'].widget.attrs.update({'type':'text' ,'class':'form-control' , 'placeholder':'Tipo'})
        self.fields['foto'].widget = forms.FileInput()
        self.fields['precio'].widget.attrs.update({'class':'form-control'})
        self.fields['descripcion'].widget.attrs.update({'type':'text' ,'class':'form-control', 'placeholder':'Descripcion'})

    def clean(self):
        cleaned_data = super(formPlato, self).clean()

        precio = cleaned_data.get('precio')

        if precio < 0:
            msg = "El precio de un plato no puede ser negativo!."
            self.add_error('precio',msg)

        return cleaned_data
'''
      Forma para la relacion posee
'''
class formPosee(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(formPosee , self).__init__(*args, **kwargs)

        self.fields['cantidad'].widget.attrs.update({'class':'form-control'})
        self.fields['idIngr'].widget.attrs.update({'type':'text' ,'class':'form-control'})
        self.fields['idIngr'].label = "Ingredientes"
    
    class Meta:
        model = posee
        exclude = ['idItem']

    def save(self,idItem):
        m = super(formPosee, self).save(commit = False)
        m.idItem = idItem
        query = posee.objects.filter(idItem = m.idItem, idIngr = m.idIngr)
        if query.exists():
            g = query[0]
            g.cantidad = m.cantidad
            g.save()
            return g
        else: 
            m.save()
            return m