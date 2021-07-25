import datetime

import click


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command()
def seed_db():
    from sqlalchemy import text

    from app import create_app
    from application.database import db
    from application.user.models import User
    from application.club.models import Club, ClubGallery, Service, ClubService, ClubWorkSchedule
    from application.funcs.password import hash_password

    app = create_app()
    db.init_app(app)

    # users
    with app.app_context():
        user_1 = User(
            username='username #1',
            firstname='first name #1',
            password=hash_password('test_password'),
            lastname='lastname #1',
            phone='+79011111111',
            email='test@test.com',
            avatar='https://via.placeholder.com/350x350',
            date_of_birth=datetime.date(year=1990, month=1, day=1)
        )

        user_2 = User(
            username='username #2',
            firstname='first name #2',
            password=hash_password('test_password2'),
            lastname='lastname #2',
            phone='+79011111112',
            email='test@test2.com',
            avatar='https://via.placeholder.com/350x350',
            date_of_birth=datetime.date(year=1989, month=1, day=1),
            enabled=False
        )
        try:
            db.session.add(user_1)
            db.session.add(user_2)
            db.session.commit()
        except:
            db.session.rollback()

        # clubs

        club_1 = Club(
            name='X-FIT Алтуфьево',
            address='г. Москва, ул. Угличская, д. 13, корп. 1, Лианозовский парк',
            phone='+7 (499) 682 72 66',
            lng=float(37.566072),
            lat=float(55.901753),
            about='Клуб в Алтуфьево в Москве',
            point=text("ST_GeomFromEWKT('SRID=4326;POINT(37.566072 55.901753)')"),
        )

        club_2 = Club(
            name='X-FIT Столешников',
            address='г. Москва, ул. Большая Дмитровка, д. 13',
            phone='+7 (495) 966 14 80',
            lng=float(37.613323),
            lat=float(55.762348),
            about='Клуб в Столешникове в Москве',
            point=text("ST_GeomFromEWKT('SRID=4326;POINT(37.613323 55.762348)')"),      # SRID 4326 - longitude and latitude
        )

        club_3 = Club(
            name='X-FIT ПАРК ПОБЕДЫ',
            address='г. Москва, ул. Василисы Кожиной, д. 1',
            phone='+7 (495) 780-84-64',
            lng=float(37.505166),
            lat=float(55.737527),
            about='Клуб у метро Парк Победы в Москве',
            point=text("ST_GeomFromEWKT('SRID=4326;POINT(37.505166 55.737527)')"),
        )
        try:
            db.session.add(club_1)
            db.session.add(club_2)
            db.session.add(club_3)
            db.session.commit()
        except Exception as e:
            print('ERROR ADD CLUBS')
            print(e)
            db.session.rollback()

        # images clubs
        club_gallery_1 = ClubGallery(
            name='Фото зала #1',
            image='https://ychef.files.bbci.co.uk/1376x774/p07ztf1q.jpg',
            club_id=club_1.id,
        )
        club_gallery_2 = ClubGallery(
            name='Фото зала #2',
            image='https://www.papersok.com/wp-content/uploads/2021/05/young-woman-performing-pushups-indoors-768.jpg',
            club_id=club_1.id,
        )
        club_gallery_3 = ClubGallery(
            name='Фото зала #1',
            image='https://www.timeoutdubai.com/public/images/2020/04/01/Fitness.jpg',
            club_id=club_2.id,
        )
        club_gallery_4 = ClubGallery(
            name='Фото зала #1',
            image='https://torontolife.com/wp-content/uploads/2020/09/A59U9082-2_B.jpg',
            club_id=club_2.id,
        )
        club_gallery_5 = ClubGallery(
            name='Logo',
            image='https://www.xfit.ru/upload/medialibrary/e8a/x-fit_fitness_clubs_small2.png',
            club_id=club_3.id,
        )
        try:
            db.session.add(club_gallery_1)
            db.session.add(club_gallery_2)
            db.session.add(club_gallery_3)
            db.session.add(club_gallery_4)
            db.session.add(club_gallery_5)
            db.session.commit()
        except Exception as e:
            print('ERROR ADD GALLERY')
            print(e)
            db.session.rollback()

        # services
        service_1 = Service(
            name='Посещение зала (в минуту)',
            about='Классические посещение зала'
        )
        service_2 = Service(
            name='Посещение SPA',
            about='Классические посещение SPA'
        )
        service_3 = Service(
            name='Тренер',
            about='Услуги тренера'
        )
        service_4 = Service(
            name='Посещение бассейна',
            about='Услуга посещения бассейна'
        )
        service_5 = Service(
            name='Солярий',
            about='Услуга солярия'
        )
        try:
            db.session.add(service_1)
            db.session.add(service_2)
            db.session.add(service_3)
            db.session.add(service_4)
            db.session.add(service_5)
            db.session.commit()
        except Exception as e:
            print('ERROR ADD SERVICES')
            print(e)
            db.session.rollback()

        # club services
        # Club #1
        club_service_1_1 = ClubService(
            club_id=club_1.id,
            service_id=service_1.id,
            price=10.0
        )
        club_service_1_2 = ClubService(
            club_id=club_1.id,
            service_id=service_2.id,
            price=2500.0
        )
        club_service_1_3 = ClubService(
            club_id=club_1.id,
            service_id=service_3.id,
            price=1500.0
        )
        club_service_1_4 = ClubService(
            club_id=club_1.id,
            service_id=service_4.id,
            price=1000.0
        )
        club_service_1_5 = ClubService(
            club_id=club_1.id,
            service_id=service_5.id,
            price=100.0
        )
        ###### Club #2
        club_service_2_1 = ClubService(
            club_id=club_2.id,
            service_id=service_1.id,
            price=10.0
        )
        club_service_2_2 = ClubService(
            club_id=club_2.id,
            service_id=service_2.id,
            price=2300.0
        )
        club_service_2_3 = ClubService(
            club_id=club_2.id,
            service_id=service_3.id,
            price=1650.0
        )
        ###### Club #3 ################
        club_service_3_1 = ClubService(
            club_id=club_3.id,
            service_id=service_1.id,
            price=12.0
        )
        club_service_3_2 = ClubService(
            club_id=club_3.id,
            service_id=service_2.id,
            price=2000.0
        )
        club_service_3_3 = ClubService(
            club_id=club_3.id,
            service_id=service_3.id,
            price=1300.0
        )
        try:
            db.session.add(club_service_1_1)
            db.session.add(club_service_1_2)
            db.session.add(club_service_1_3)
            db.session.add(club_service_1_4)
            db.session.add(club_service_1_5)
            db.session.add(club_service_2_1)
            db.session.add(club_service_2_2)
            db.session.add(club_service_2_3)
            db.session.add(club_service_3_1)
            db.session.add(club_service_3_2)
            db.session.add(club_service_3_3)
            db.session.commit()
        except Exception as e:
            print('ERROR ADD SERVICES')
            print(e)
            db.session.rollback()
        #
        # monday = 'monday'
        # tuesday = 'tuesday'
        # wednesday = 'wednesday'
        # thursday = 'thursday'
        # friday = 'friday'
        # saturday = 'saturday'
        # sunday = 'sunday'

        hours_club_1_1 = ClubWorkSchedule(day='monday', work_hours='09:00-22:00', club_id=club_1.id)
        hours_club_1_2 = ClubWorkSchedule(day='tuesday', work_hours='09:00-22:00', club_id=club_1.id)
        hours_club_1_3 = ClubWorkSchedule(day='wednesday', work_hours='09:00-22:00', club_id=club_1.id)
        hours_club_1_4 = ClubWorkSchedule(day='thursday', work_hours='09:00-22:00', club_id=club_1.id)
        hours_club_1_5 = ClubWorkSchedule(day='friday', work_hours='09:00-22:00', club_id=club_1.id)
        hours_club_1_6 = ClubWorkSchedule(day='saturday', work_hours='09:00-21:00', club_id=club_1.id)
        hours_club_1_7 = ClubWorkSchedule(day='sunday', work_hours='09:00-21:00', club_id=club_1.id)

        hours_club_2_1 = ClubWorkSchedule(day='monday', work_hours='09:30-22:00', club_id=club_2.id)
        hours_club_2_2 = ClubWorkSchedule(day='tuesday', work_hours='09:30-22:00', club_id=club_2.id)
        hours_club_2_3 = ClubWorkSchedule(day='wednesday', work_hours='09:30-22:00', club_id=club_2.id)
        hours_club_2_4 = ClubWorkSchedule(day='thursday', work_hours='09:30-22:00', club_id=club_2.id)
        hours_club_2_5 = ClubWorkSchedule(day='friday', work_hours='09:30-22:00', club_id=club_2.id)
        hours_club_2_6 = ClubWorkSchedule(day='saturday', work_hours='09:30-22:00', club_id=club_2.id)
        hours_club_2_7 = ClubWorkSchedule(day='sunday', work_hours='09:30-22:00', club_id=club_2.id)

        hours_club_3_1 = ClubWorkSchedule(day='monday', work_hours='08:30-22:30', club_id=club_3.id)
        hours_club_3_2 = ClubWorkSchedule(day='tuesday', work_hours='08:30-22:30', club_id=club_3.id)
        hours_club_3_3 = ClubWorkSchedule(day='wednesday', work_hours='08:30-22:30', club_id=club_3.id)
        hours_club_3_4 = ClubWorkSchedule(day='thursday', work_hours='08:30-22:30', club_id=club_3.id)
        hours_club_3_5 = ClubWorkSchedule(day='friday', work_hours='08:30-22:30', club_id=club_3.id)
        hours_club_3_6 = ClubWorkSchedule(day='saturday', work_hours='08:30-22:30', club_id=club_3.id)
        hours_club_3_7 = ClubWorkSchedule(day='sunday', work_hours='08:30-22:30', club_id=club_3.id)

        work_hours_models = [
            hours_club_1_1, hours_club_1_2, hours_club_1_3, hours_club_1_4, hours_club_1_5, hours_club_1_6, hours_club_1_7,
            hours_club_2_1, hours_club_2_2, hours_club_2_3, hours_club_2_4, hours_club_2_5, hours_club_2_6, hours_club_2_7,
            hours_club_3_1, hours_club_3_2, hours_club_3_3, hours_club_3_4, hours_club_3_5, hours_club_3_6, hours_club_3_7,
        ]
        try:
            for work_hours in work_hours_models:
                db.session.add(work_hours)
            db.session.commit()
        except Exception as e:
            print('ERROR ADD WORK HOURS!')
            print(e)
            db.session.rollback()

@cli.command()
def seed_pages():
    from application import create_app
    from application.database import db
    from application.content.models import PublicPage

    app = create_app()
    db.init_app(app)

    # users
    with app.app_context():
        privacy_page = PublicPage(
            slug='privacy',
            title='Политика конфиденциальности',
            h1='h1 политика',
            meta_description='Политика конфиденциальности',
            body='Большой текст с политикой',
        )
        rules_page = PublicPage(
            slug='rules',
            title='Правила пользования сервисом',
            h1='h1 правила',
            meta_description='Правила пользования сервисом',
            body='Большой текст с правилами',
        )
        try:
            db.session.add(privacy_page)
            db.session.add(rules_page)
            db.session.commit()
        except Exception as e:
            print('ERROR ADD PUBLIC PAGES')
            print(e)
            db.session.rollback()

@cli.command()
def clear_tables():
    from application import create_app
    from application.database import db

    app = create_app()
    db.init_app(app)

    # users
    with app.app_context():
        db.session.execute(""" 
            TRUNCATE TABLE public.club RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.club_gallery RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.club_gallery RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.club_work_schedules RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.service RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.club_service RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.page RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.order RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.order_service RESTART IDENTITY CASCADE;
            TRUNCATE TABLE public.user RESTART IDENTITY CASCADE;
        """)
        db.session.commit()

if __name__ == '__main__':
    cli()
