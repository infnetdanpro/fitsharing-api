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
    from application.club.models import Club, ClubGallery, Service, ClubService
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
            lat=float(0.0),
            lng=float(0.0),
            about='Клуб в Алтуфьево в Москве',
            point=text("ST_GeomFromEWKT('SRID=4326;POINT(37.566072 55.901753)')"),
        )

        club_2 = Club(
            name='X-FIT Столешников',
            address='г. Москва, ул. Большая Дмитровка, д. 13',
            phone='+7 (495) 966 14 80',
            lat=float(0.0),
            lng=float(0.0),
            about='Клуб в Столешникове в Москве',
            point=text("ST_GeomFromEWKT('SRID=4326;POINT(37.613323 55.762348)')"),
        )

        club_3 = Club(
            name='X-FIT ПАРК ПОБЕДЫ',
            address='г. Москва, ул. Василисы Кожиной, д. 1',
            phone='+7 (495) 780-84-64',
            lat=float(0.0),
            lng=float(0.0),
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

if __name__ == '__main__':
    cli()
