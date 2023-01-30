from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from django.urls import reverse
from django.contrib.auth.models import User
from .managers import ZManager, CategoryManager


class AuthorType(models.Model):
    """
    Класс для описания вида авторов
    """
    title = 'Вид Автора'
    name = models.CharField(max_length=128,
                            verbose_name='Вид авторов')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид авторов'
        verbose_name_plural = 'Виды авторов'


class Author(models.Model):
    """
    Класс для описания авторов
    """
    title = 'Автор'
    name = models.CharField(max_length=128,
                            verbose_name='Имя')
    info = models.TextField(max_length=2048,
                            blank=True,
                            null=True,
                            verbose_name='Сведения об авторе'
                            )
    photo = models.ImageField(upload_to='photos/authors/',
                              verbose_name='Фото',
                              blank=True,
                              null=True
                              )
    atype = models.ForeignKey(AuthorType,
                              on_delete=models.PROTECT,
                              verbose_name='Вид автора',
                              blank=True,
                              null=True
                              )
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Category(MPTTModel):
    """
    Категория (рубрика), к которой относится знание.
    Иерархическая структура.
    """
    title = 'Категория'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children'
                            )
    content = models.TextField(max_length=1024,
                               blank=True,
                               null=True,
                               verbose_name='Содержание'
                               )
    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )
    # менеджеры объектов
    tree_objects = TreeManager()
    published = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('drevo_type', kwargs={"pk": self.pk})

    def has_published_children(self) -> bool():
        """
        Возвращает True, если среди потомков объекта имеются опубликованные,
        False в противном случае.
        """
        children = self.get_children()
        for child in children:
            if child.is_published:
                return True
        return False

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class MPTTMeta:
        order_insertion_by = ['name']


class Tz(models.Model):
    """
    Виды знания
    """
    title = 'Вид знания'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')
    order = models.PositiveSmallIntegerField(
                                verbose_name='Порядок',
                                help_text='укажите порядковый номер',
                                default=0,
                                blank=True
                                )                                  
    is_systemic = models.BooleanField(default=False,
                                      verbose_name='Системный?')                                

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид знания'
        verbose_name_plural = 'Виды знания'
        ordering = ('order', )


class Label(models.Model):
    """
    Метки
    """
    title = 'Метка'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки'
        ordering = ('name',)


class Znanie(models.Model):
    """
    Класс для описания сущности 'Знание'
    """
    title = 'Знание'
    name = models.CharField(max_length=256,
                            verbose_name='Тема',
                            unique=True
                            )
    category = TreeForeignKey(Category,
                              on_delete=models.PROTECT,
                              verbose_name='Категория',
                              null=True,
                              blank=True,
                              limit_choices_to={'is_published': True}
                              )
    tz = models.ForeignKey(Tz,
                           on_delete=models.PROTECT,
                           verbose_name='Вид знания'
                           )
    content = models.TextField(max_length=2048,
                               blank=True,
                               null=True,
                               verbose_name='Содержание'
                               )
    href = models.URLField(max_length=256,
                           verbose_name='Источник',
                           help_text='укажите www-адрес источника',
                           null=True,
                           blank=True)
    source_com = models.CharField(max_length=256,
                                  verbose_name='Комментарий к источнику',
                                  null=True,
                                  blank=True
                                  )
    author = models.ForeignKey(Author,
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора',
                               null=True,
                               blank=True
                               )
    date = models.DateField(auto_now_add=True,
                            verbose_name='Дата создания',
                            )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата и время редактирования',
                                      )
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT,
                             editable=False,
                             verbose_name='Пользователь'
                             )
    order = models.IntegerField(verbose_name='Порядок',
                                help_text='укажите порядковый номер',
                                null=True,
                                blank=True
                                )

    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )
    labels = models.ManyToManyField(Label,
                                    verbose_name='Метки',
                                    blank=True
                                    )
    # Для обработки записей (сортировка, фильтрация) вызывается собственный Manager,
    # в котором уже установлена фильтрация по is_published и сортировка
    objects = models.Manager()
    published = ZManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('zdetail', kwargs={"pk": self.pk})

    def voting(self, user, value):
        rating_obj = self.znrating_set.filter(user=user).first()

        if rating_obj:
            if value == rating_obj.value:
                rating_obj.value = ZnRating.BLANK
            else:
                rating_obj.value = value

            rating_obj.save()
        else:
            ZnRating.objects.create(znanie=self, user=user, value=value)

    def get_users_vote(self, user):
        rating_obj = self.znrating_set.filter(user=user).first()

        if rating_obj:
            if rating_obj.value in (ZnRating.LIKE, ZnRating.DISLIKE):
                return rating_obj.value

        return None

    def get_likes_count(self):
        return self.znrating_set.filter(value=ZnRating.LIKE).count()

    def get_dislikes_count(self):
        return self.znrating_set.filter(value=ZnRating.DISLIKE).count()

    class Meta:
        verbose_name = 'Знание'
        verbose_name_plural = 'Знания'
        ordering = ('order',)


class IP(models.Model):
    """
    IP пользавателей
    """
    title = 'IP'
    visits = models.ManyToManyField(Znanie,
                                    verbose_name='ID',
                                    blank=True
                                    )
    ip = models.CharField(max_length=100)


class ZnImage(models.Model):
    znanie = models.ForeignKey(Znanie,
                               related_name='photos',
                               on_delete=models.PROTECT
                               )
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/',
                              verbose_name='Фото',
                              blank=True
                              )

    def __str__(self):
        zn_name = str(self.znanie)[:40]
        return f'Фото № {self.id} для "{zn_name}"'


class Tr(models.Model):
    """
    Виды связей
    """
    title = 'Вид связи'
    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            unique=True
                            )
    order = models.PositiveSmallIntegerField(
                                verbose_name='Порядок',
                                help_text='укажите порядковый номер',
                                default=0,
                                )
    is_systemic = models.BooleanField(default=False,
                                      verbose_name='Системный?')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид связи'
        verbose_name_plural = 'Виды связи'
        ordering = ('order', 'name',)


class Relation(models.Model):
    """
    Класс для связи Знание-Знание
    """
    title = 'Связь'
    # связанное знание
    bz = models.ForeignKey(Znanie,
                           on_delete=models.PROTECT,
                           verbose_name='Базовое знание',
                           help_text='укажите базовое знание',
                           related_name='base'
                           )
    tr = models.ForeignKey(Tr,
                           on_delete=models.PROTECT,
                           verbose_name='Вид связи',
                           help_text='укажите вид связи'
                           )
    rz = models.ForeignKey(Znanie,
                           on_delete=models.PROTECT,
                           verbose_name='Связанное знание',
                           help_text='укажите связанное знание',
                           related_name='related'
                           )
    author = models.ForeignKey(Author,
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора'
                               )
    date = models.DateField(auto_now_add=True,
                            verbose_name='Дата создания',
                            )
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT,
                             editable=False,
                             verbose_name='Пользователь'
                             )
    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )                             
    objects = models.Manager()

    def __str__(self):
        return f"{self.title} {self.bz.pk}-{self.bz}-{self.rz.pk}"

    class Meta:
        verbose_name = 'Связь'
        verbose_name_plural = 'Связи'
        ordering = ('-date',)


class GlossaryTerm(models.Model):
    """
    Класс для описания термина глоссария
    """
    title = 'Термин глоссария'
    name = models.CharField(max_length=256,
                            verbose_name='Термин',
                            unique=True
                            )
    description = models.TextField(max_length=2048,
                                    blank=True,
                                    null=True,
                                    verbose_name='Описание'
                                    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата и время создания',
                                     )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата и время редактирования',
                                      )

    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано?'
                                       )
    objects = models.Manager()

    def __str__(self):
        return self.name   

    class Meta:
        verbose_name = 'Термин глоссария'
        verbose_name_plural = 'Термины глоссария'
        ordering = ('name',)


class ZnRating(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    BLANK = ''

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь'
                             )
    znanie = models.ForeignKey(Znanie,
                               on_delete=models.CASCADE,
                               verbose_name='Знание'
                               )
    value = models.CharField(max_length=7,
                             blank=True,
                             verbose_name='Значение'
                             )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата и время создания',
                                      )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата и время изменения',
                                      )

    class Meta:
        unique_together = ('user', 'znanie')
