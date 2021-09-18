from flask import render_template, request, jsonify
from flask_login import current_user
from sqlalchemy import or_

from application import Club, VerifiedUsersByClub
from application.club_admin.forms import VerificationUserForm
from application.models.club_user.models import ClubUserAssociation
from application.database import db

from application.club_admin.utils import auth_only


@auth_only
def main_view():
    context = {}
    title = 'Главная страница'
    context.update(title=title)

    # getting related clubs by current_user
    club_associations = db.session.query(ClubUserAssociation)\
        .filter(ClubUserAssociation.club_user_id == current_user.id)\
        .join(Club)\
        .filter(Club.enabled.is_(True))\
        .all()
    context.update(club_associations=club_associations)
    return render_template('club_admin/cards.html', **context)


@auth_only
def club_view():
    args = request.args
    context = {}

    # getting related clubs by current_user
    clubs = db.session.query(ClubUserAssociation)\
        .filter(ClubUserAssociation.club_user_id == current_user.id, ClubUserAssociation.club_id == args['club_id'])\
        .join(Club) \
        .filter(Club.enabled.is_(True)) \
        .all()
    context.update(title=f'Посетители в: {clubs[0].club.name}')
    context.update(club_associations=clubs)
    return render_template('club_admin/cards_one.html', **context)


@auth_only
def verification_users_list():
    # Show requests to verificate info about user
    title = 'Главная страница'
    context = dict(title=title)

    cus = db.session.query(ClubUserAssociation.club_id) \
        .filter(ClubUserAssociation.club_user_id == current_user.id) \
        .join(Club) \
        .filter(Club.enabled.is_(True)) \
        .all()

    club_ids = [ca.club_id for ca in cus]

    verifications = db.session.query(VerifiedUsersByClub)\
        .filter(VerifiedUsersByClub.club_id.in_(club_ids),
                or_(
                    VerifiedUsersByClub.complete.is_(False),
                    VerifiedUsersByClub.complete.is_(None))
                )\
        .all()
    context.update(verifications=verifications)
    return render_template('club_admin/tables.html', **context)


@auth_only
def verification_user():
    title = 'Верификация пользователя'
    context = dict(title=title)

    user_form = VerificationUserForm(request.form)

    cus = db.session.query(ClubUserAssociation.club_id) \
        .filter(ClubUserAssociation.club_user_id == current_user.id) \
        .join(Club) \
        .filter(Club.enabled.is_(True)) \
        .all()

    club_ids = [ca.club_id for ca in cus]

    user_for_verification = db.session.query(VerifiedUsersByClub) \
        .filter(
            VerifiedUsersByClub.user_id == request.args.get('user_id'),
            VerifiedUsersByClub.club_id.in_(club_ids)
        ).first()

    if request.method == 'POST' and user_form.validate():
        user_for_verification.user_verify.firstname = user_form.firstname.data
        user_for_verification.user_verify.lastname = user_form.lastname.data
        user_for_verification.user_verify.email = user_form.email.data
        user_for_verification.user_verify.phone = user_form.phone.data
        user_for_verification.user_verify.date_of_birth = user_form.date_of_birth.data

        user_for_verification.complete = True
        user_for_verification.verified_by_club_user_id = current_user.id
        db.session.add(user_for_verification)
        db.session.commit()
    print(user_form.email.data)
    print(user_form.date_of_birth.data)
    print(user_form.errors)
    user_form.firstname = user_for_verification.user_verify.firstname
    user_form.lastname = user_for_verification.user_verify.lastname
    user_form.email = user_for_verification.user_verify.email
    user_form.phone = user_for_verification.user_verify.phone
    user_form.date_of_birth = user_for_verification.user_verify.date_of_birth
    user_id = request.args.get('user_id')

    context.update(user_for_verification=user_for_verification, user_form=user_form, user_id=user_id)
    return render_template('club_admin/user_verification.html', **context)


@auth_only
def verification_users_count():
    cus = db.session.query(ClubUserAssociation.club_id) \
        .filter(ClubUserAssociation.club_user_id == current_user.id) \
        .join(Club) \
        .filter(Club.enabled.is_(True)) \
        .all()

    club_ids = [ca.club_id for ca in cus]

    verifications = db.session.query(VerifiedUsersByClub.id) \
        .filter(VerifiedUsersByClub.club_id.in_(club_ids)) \
        .count()
    return jsonify({'verification_request_count': verifications})


# @auth_only
# def add_club_view():
#     context = {}
#     title = 'Добавление клуба'
#     context.update(title=title)
#
#     if request.method == 'POST':
#         print(request.form)
#
#     return render_template('club_admin/add_club.html', **context)
