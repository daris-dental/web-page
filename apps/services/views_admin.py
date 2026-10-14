from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ServicioForm, ArticuloForm
from .models import Servicio, Articulo


@staff_member_required
def lista(request):
    servicios = Servicio.objects.all().order_by('-activo', 'nombre')
    return render(request, 'panel/servicios_lista.html', {'servicios': servicios})


@staff_member_required
def crear(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio creado correctamente.')
            return redirect('panel:servicios_lista')
    else:
        form = ServicioForm()
    return render(request, 'panel/servicios_form.html', {
        'form': form, 'accion': 'Crear'
    })


@staff_member_required
def editar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)  # ← FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado.')
            return redirect('panel:servicios_lista')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'panel/servicios_form.html', {
        'form': form, 'accion': 'Editar', 'servicio': servicio
    })

@staff_member_required
def eliminar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        nombre = servicio.nombre
        servicio.delete()
        messages.success(request, f'Servicio «{nombre}» eliminado.')
        return redirect('panel:servicios_lista')
    return render(request, 'panel/confirmar_eliminar.html', {
        'objeto': servicio, 'titulo': 'servicio',
        'cancelar_url': 'panel:servicios_lista',
    })


# --- Artículos ---

@staff_member_required
def articulos_lista(request):
    articulos = Articulo.objects.all().order_by('-activo', 'nombre')
    return render(request, 'panel/articulos_lista.html', {'articulos': articulos})


@staff_member_required
def articulos_crear(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artículo creado correctamente.')
            return redirect('panel:articulos_lista')
    else:
        form = ArticuloForm()
    return render(request, 'panel/articulos_form.html', {
        'form': form, 'accion': 'Crear',
    })


@staff_member_required
def articulos_editar(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES, instance=articulo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artículo actualizado.')
            return redirect('panel:articulos_lista')
    else:
        form = ArticuloForm(instance=articulo)
    return render(request, 'panel/articulos_form.html', {
        'form': form, 'accion': 'Editar', 'articulo': articulo,
    })


@staff_member_required
def articulos_eliminar(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    if request.method == 'POST':
        nombre = articulo.nombre
        articulo.delete()
        messages.success(request, f'Artículo «{nombre}» eliminado.')
        return redirect('panel:articulos_lista')
    return render(request, 'panel/confirmar_eliminar.html', {
        'objeto': articulo, 'titulo': 'artículo',
        'cancelar_url': 'panel:articulos_lista',
    })