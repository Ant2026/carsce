from django.urls import path
from inicio_sesion import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.foro, name="foro"),
    path('inicio_sesion/', views.autenticacion, name="inicio_sesion"),
    path('panel_usuario/', views.panel_usuario, name="panel_usuario"),
    path('panel_registro/', views.panel_registro, name="panel_registro"),
    path('cerrar_sesion/', views.cerrar_sesion, name="cerrar_sesion"),
    path('comp_registro/', views.comp_registro, name="comp_registro"),
    path('datos_usr_admin/', views.datos_usr_admin, name="datos_usr_admin"),
    path('validar_ci_auxiliar/', views.validar_ci_auxiliar, name="validar_ci_auxiliar"),
    path('validar_cod_opsu/', views.validar_cod_opsu, name="validar_cod_opsu"),
    path('validar_ci_usr/', views.validar_ci_usr, name="validar_ci_usr"),
    path('validar_email/', views.validar_email, name="validar_email"),
    path('panel_registro/', views.panel_registro, name="panel_registro"),
    path('val_usuario/', views.val_usuario, name="val_usuario"),
    path('val_password/', views.val_password, name="val_password"),
    path('registro_est/', views.registro_est, name="registro_est"),
    path('confirmar_reg/', views.confirmar_reg, name="confirmar_reg"),
    path('guardar_cred/', views.guardar_cred, name="guardar_cred"),
    path('pnfs_cursar/', views.pnfs_cursar, name="pnfs_cursar"),
    path('pre_reg_personal/', views.pre_reg_personal, name="pre_reg_personal"),
    path('datos_perfiles/', views.datos_perfiles, name="datos_perfiles"),

    path('pnfs_disp/', views.pnfs_disp, name="pnfs_disp"),
    path('pnfs_reg/', views.pnfs_reg, name="pnfs_reg"),
    path('datos_pnf/', views.datos_pnf, name="datos_pnf"),
    path('act_pnf/', views.act_pnf, name="act_pnf"),
    path('reg_pnf/', views.reg_pnf, name="reg_pnf"),
    path('nombre_pnf/', views.nombre_pnf, name="nombre_pnf"),
    path('codigo_pnf/', views.codigo_pnf, name="codigo_pnf"),
    path('ver_pnf/', views.ver_pnf, name="ver_pnf"),

    path('nombre_materia/', views.nombre_materia, name="nombre_materia"),
    path('codigo_materia/', views.codigo_materia, name="codigo_materia"),
    path('mat_lista/', views.mat_lista, name="mat_lista"),
    path('mat_datos/', views.mat_datos, name="mat_datos"),
    path('mat_guardar/', views.mat_guardar, name="mat_guardar"),
    path('reg_mat/', views.reg_mat, name="reg_mat"),

    path('reg_calendario/', views.reg_calendario, name="reg_calendario"),
    path('periodos_lista/', views.periodos_lista, name="periodos_lista"),
    path('calendarios_lista/', views.calendarios_lista, name="calendarios_lista"),
    path('calendario_datos/', views.calendario_datos, name="calendario_datos"),
    path('calendario_guardar/', views.calendario_guardar, name="calendario_guardar"),

    path('auts_reg/', views.auts_reg, name="auts_reg"),
    path('datos_aut/', views.datos_aut, name="datos_aut"),
    path('act_datos_aut/', views.act_datos_aut, name="act_datos_aut"),
    path('cargo_asig_aut/', views.cargo_asig_aut, name="cargo_asig_aut"),
    path('val_ci_aut/', views.val_ci_aut, name="val_ci_aut"),
    path('cargo_user/', views.cargo_user, name="cargo_user"),
    path('act_cargo_aut/', views.act_cargo_aut, name="act_cargo_aut"),
    path('val_resolucion/', views.val_resolucion, name="val_resolucion"),
    path('vist_auts/', views.vist_auts, name="vist_auts"),
    path('reasig_cargo/', views.reasig_cargo, name="reasig_cargo"),
    path('reg_auts/', views.reg_auts, name="reg_auts"),

    path('aulas_reg/', views.aulas_reg, name="aulas_reg"),
    path('datos_a/', views.datos_a, name="datos_a"),
    path('act_aula_acad/', views.act_aula_acad, name="act_aula_acad"),
    path('reg_aula/', views.reg_aula, name="reg_aula"),
    path('val_aula/', views.val_aula, name="val_aula"),

    path('sec_reg/', views.sec_reg, name="sec_reg"),
    path('datos_sec/', views.datos_sec, name="datos_sec"),
    path('guardar_act_sec/', views.guardar_act_sec, name="guardar_act_sec"),
    path('reg_sec/', views.reg_sec, name="reg_sec"),
    path('val_sec/', views.val_sec, name="val_sec"),

    path('docs_reg/', views.docs_reg, name="docs_reg"),
    path('mats_reg/', views.mats_reg, name="mats_reg"),
    path('asig_mat_doc/', views.asig_mat_doc, name="asig_mat_doc"),
    path('busc_mat/', views.busc_mat, name="busc_mat"),
    path('act_asig/', views.act_asig, name="act_asig"),
    path('pnf_per_acad/', views.pnf_per_acad, name="pnf_per_acad"),

    path('dat_usr/', views.dat_usr, name="dat_usr"),
    path('corr_usr/', views.corr_usr, name="corr_usr"),
    path('env_cod_act_corr/', views.env_cod_act_corr, name="env_cod_act_corr"),
    path('aut_act_corr/', views.aut_act_corr, name="aut_act_corr"),
    path('act_dat_usr/', views.act_dat_usr, name="act_dat_usr"),

    path('bus_usr/', views.bus_usr, name="bus_usr"),
    path('comp_usr/', views.comp_usr, name="comp_usr"),
    path('env_cod_usr/', views.env_cod_usr, name="env_cod_usr"),
    path('comp_cod_usr/', views.comp_cod_usr, name="comp_cod_usr"),
    path('val_cod/', views.val_cod, name="val_cod"),
    path('reenv_cod_btn/', views.reenv_cod_btn, name="reenv_cod_btn"),
    path('env_cod_ver/', views.env_cod_ver, name="env_cod_ver"),
    path('panel_rec_cred/', views.panel_rec_cred, name="panel_rec_cred"),
    path('rec_cont/', views.rec_cont, name="rec_cont"),
    path('rec_usr/', views.rec_usr, name="rec_usr"),
    path('exist_cod/', views.exist_cod, name="exist_cod"),
    path('corr_reg/', views.corr_reg, name="corr_reg"),

    #FORO
    path('Historia/', views.Historia, name="Historia"),
    path('mision_vision/', views.mision_vision, name="mision_vision"),
    path('pst/', views.pst, name="pst"),
    path('psc/', views.psc, name="psc"),
    path('trayectoria/', views.trayectoria, name="trayectoria"),
    path('carreras_impartidas/', views.carreras_impartidas, name="carreras_impartidas"),
    path('Planificacion_Docente/', views.Planificacion_Docente, name="Planificacion_Docente"),

    path('barra_lateral/', views.barra_lateral, name="barra_lateral"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )