from django.contrib import admin
from . import models
# Register your models here.

class VariacaoInline(admin.TabularInline):
    model = models.Variacao
    extra = 1

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome','descricao_pequena', 'preco_marketing','preco_marketing_promocional']
    inlines = [
        VariacaoInline,
    ]

admin.site.register(models.Produto,ProdutoAdmin)
admin.site.register(models.Variacao)