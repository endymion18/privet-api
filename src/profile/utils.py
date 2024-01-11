import uuid

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.profile.models import Student, Buddy, Contacts, Language, LanguagesRelationship, Country
from src.profile.schemas import BuddyProfile, StudentProfile, ContactSchema, ChangeUserInfo


async def get_user_profile(current_user: User, session: AsyncSession):
    profile_type = current_user.role_id
    if profile_type == 1:
        table = Student
    else:
        table = Buddy
    profile_info = await session.execute(select(table).where(table.user_id == current_user.id))

    if profile_info.scalar() is None:
        add_profile = insert(table).values(user_id=current_user.id)
        contacts = await session.execute(select(Contacts).where(Contacts.user_id == current_user.id))
        if contacts.scalar() is None:
            add_contacts = insert(Contacts).values(user_id=current_user.id, email=current_user.email)
            await session.execute(add_contacts)
        await session.execute(add_profile)
        await session.commit()
    profile_info = await session.execute(select(table).where(table.user_id == current_user.id))

    user_profile = await create_user_profile(profile_info.scalar(), profile_type)

    other_languages = await session.execute(
        select(LanguagesRelationship.language).where(LanguagesRelationship.user_id == current_user.id))
    other_languages = other_languages.scalars().all()
    other_languages_names = []
    if len(other_languages) != 0:
        for language_id in other_languages:
            language_name = await session.execute(select(Language.id).where(
                Language.id == language_id))
            language_name = language_name.scalar()
            other_languages_names.append(language_name)

    contacts = await session.execute(select(Contacts).where(Contacts.user_id == current_user.id))
    contacts = ContactSchema(contacts.scalar())

    return {
        "profile_info": user_profile,
        "contacts": contacts,
        "other_languages": other_languages_names
    }


async def create_user_profile(profile_info: Buddy | Student,
                              profile_type: int
                              ) -> BuddyProfile | StudentProfile:
    if profile_type == 1:
        profile = StudentProfile
    else:
        profile = BuddyProfile

    created_profile = profile(profile_info)
    return created_profile


async def update_user_info(user_info: ChangeUserInfo,
                           current_user: User,
                           session: AsyncSession):
    profile_type = current_user.role_id
    if profile_type == 1:
        table = Student
    else:
        table = Buddy

    info = user_info

    if profile_type == 1:
        await session.execute(update(table).where(table.user_id == current_user.id).values(
            full_name=info.full_name,
            citizenship=info.citizenship,
            sex=info.sex,
            birthdate=info.birthdate,
            native_language=info.native_language,
            university=info.university
        ))
    else:
        await session.execute(update(table).where(table.user_id == current_user.id).values(
            full_name=info.full_name,
            city=info.city,
            sex=info.sex,
            birthdate=info.birthdate,
            native_language=info.native_language,
            university=info.university
        ))

    await session.execute(update(Contacts).where(Contacts.user_id == current_user.id).values(
        phone=info.phone,
        telegram=info.telegram,
        whatsapp=info.whatsapp,
        vk=info.vk
    ))

    await session.execute(delete(LanguagesRelationship).where(LanguagesRelationship.user_id == current_user.id))
    await session.commit()

    if len(info.other_languages_ids) != 0:
        languages = [{"user_id": current_user.id, "language": language_id} for language_id in info.other_languages_ids]
        await session.execute(insert(LanguagesRelationship).values(languages))
    await session.commit()

    return await get_user_profile(current_user, session)


async def get_languages(session: AsyncSession):
    languages = await session.execute(select(Language))
    languages = languages.scalars().all()
    return languages


async def get_language(language_id: int, session: AsyncSession):
    language = await session.execute(select(Language.name).where(Language.id == language_id))
    language = language.scalar()
    return language


async def get_languages_by_id(languages_ids: list[int], session: AsyncSession):
    languages = await session.execute(select(Language.name).where(Language.id.in_(languages_ids)))
    languages = languages.scalars().all()
    return languages


async def get_countries(session: AsyncSession):
    countries = await session.execute(select(Country))
    countries = countries.scalars().all()
    return countries


async def get_country_by_id(country_id: int, session: AsyncSession):
    country = await session.execute(select(Country.name).where(Country.id == country_id))
    country = country.scalar()
    return country


async def get_user_by_uuid(user_id: uuid.UUID, session: AsyncSession):
    user = await session.execute(select(User).where(User.id == user_id))
    print(user)
    user = user.scalar()
    if user is not None:
        return user
    return None
