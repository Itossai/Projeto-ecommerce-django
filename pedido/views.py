from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib import messages
from django.views import View
from django.views.generic import DetailView

from produto.models import Variacao
from .models import Pedido,ItemPedido

from utils import utils
# Create your views here.


class DispatchLoginRequired(View):
    def dispatch(self,*args,**kwargs):
        if not self.user.is_authenticated:
            return redirect('perfil:criar')
        return super().dispatch(*args,**kwargs)

class Pagar(DispatchLoginRequired,DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'

    def get_queryset(self,*args,**kwargs):
        qs = super().get_queryset(*args,**kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs


class SalvarPedido(View):
    template_name = 'pedido/pagar.html'
    
    def get(self, *args, **kwargs):
        
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Você precisa fazer o Login."
            )
            return redirect('perfil:criar')
        
        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                "Carrinho Vazio."
            )
            self.request.session.save()
            return redirect('protudo:lista')
        
        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_ids = [v for v in carrinho]

        bd_variacoes =list(Variacao.objects.select_related('produto')
                           .filter(id_in=carrinho_variacao_ids))

        for variacao in bd_variacoes:
            vid= str(variacao.id)
            estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promocional = carrinho[vid]['preco_unitario_promocional']

            error_msg_estoque=''

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco quantitativo'] = estoque * preco_unt
                carrinho[vid]['preco quantitativo promocional'] = estoque * preco_unt_promocional
                
                error_msg_estoque = "Quantidade de alguns produtos é insuficiente" \
                    "A quantidade desses produtos foram ajustadas."\
                    "Verifique os produtos afetados a seguir."    
                
            if error_msg_estoque:    
                messages.warning(
                    self.request,
                    error_msg_estoque
                )
                return redirect('produto:carrinho')
            
        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_total_preco(carrinho)

        pedido = Pedido(
            usuario = self.request.user,
            total = valor_total_carrinho,
            qtd_total_carrinho = qtd_total_carrinho,
            status = 'C'
        )

        pedido.save()

        ItemPedido.objects.bulk_create( 
            [
                ItemPedido(
                    pedido=pedido,
                    produto = v['produto_nome'],
                    produto_id = v['produto_id'],
                    variacao = v['variacao_nome'],
                    variacao_id = v['variacao_id'],
                    preco = v['preco_quantitativo'],
                    preco_promocional = v['preco_quantitativo_promocional'],
                    quantidade = v['quantidade'],
                    imagem = v['imagem']
                ) for v in carrinho.values()
            ]
        )

        del self.request.session['carrinho']

        return redirect(
            reverse('pedido:pagar',
                kwargs={
                'pk':pedido.pk
                    }
                )
            )

class Detalhe(View):
    ...

class Lista(View):
    ...