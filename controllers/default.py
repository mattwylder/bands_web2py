# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    search = SQLFORM.factory(Field('query', 'Search:'))
    listings = db(db.listing.id > 0).select();
    return dict(search=search,listings=listings,user=user)

@auth.requires_login()
def listing():
    listing = db.listing(request.args(0,cast=int)) or redirect(URL('index'))
    user_authorized =auth.user.id == listing.created_by
    genres=db((db.listing_genre.genre_ndx== db.genre.id) & 
	     (db.listing_genre.listing_ndx == listing.id)).select(
	    db.genre.genre_name)
    roles = db((db.listing_role.role_ndx == db.role.id) &
	       (db.listing_role.listing_ndx == listing.id)).select(
	    db.role.role_name)
    audio = db((db.listing_audio.audio_ndx== db.audio.id) &
	       (db.listing_audio.listing_ndx == listing.id)).select(
	    db.audio.path_to)
    auditions = None
    if user_authorized:
	auditions = db((db.audition.created_by == db.auth_user.id) &
		    (db.audition.parent_ndx == listing.id)).select(db.audition.id,db.auth_user.first_name, db.auth_user.last_name)
    return dict(user_authorized=user_authorized,listing=listing, genres=genres,roles=roles, audio=audio, auditions=auditions)

@auth.requires_login()
def audition():
    audition = db.audition(request.args(0,cast=int)) or redirect(URL('index')) 
    author = db(db.auth_user.id==audition.created_by).select().first()
    genres = db((db.audition_genre.genre_ndx== db.genre.id) & 
	     (db.audition_genre.audition_ndx == audition.id)).select(
	    db.genre.genre_name)
    roles = db((db.audition_role.role_ndx == db.role.id) &
	       (db.audition_role.audition_ndx == audition.id)).select(
	    db.role.role_name)
    audio = db((db.audition_audio.audio_ndx== db.audio.id) &
	       (db.audition_audio.audition_ndx == audition.id)).select(
	    db.audio.path_to)
    return dict(author=author,audition=audition, genres=genres,roles=roles, audio=audio)


@auth.requires_login()
def listingform():
    form = SQLFORM.factory(
		Field('title','title',requires=IS_NOT_EMPTY()),
		Field('city','City', requires=IS_NOT_EMPTY()),
		Field('desc','description', requires=IS_NOT_EMPTY()),
		Field('roles','Roles needed (Separated by commas)'),
		Field('genres','Genres (Separated by commas)'),
		Field('audio', 'Soundcloud links(separated by commas)'))
    if form.process().accepted:    
        title = form.vars.title
	city = form.vars.city
        desc = form.vars.desc
	genres = form.vars.genres
        roles = form.vars.roles
	audio = form.vars.audio

	listing_ndx = db.listing.insert(title=title, city=city,body=desc,
				    created_by=auth.user.id) 
	for cur_genre in genres.split(','):
	    genre_ndx = db(db.genre.genre_name==cur_genre).select(db.genre.id).first()
	    if genre_ndx == None:
		genre_ndx = db.genre.insert(genre_name=cur_genre)
	    db.listing_genre.insert(listing_ndx=listing_ndx,genre_ndx=genre_ndx)

	for cur_role in roles.split(','):
	    role_ndx = db(db.role.role_name==cur_role).select(db.role.id).first()
	    if role_ndx == None:
		role_ndx = db.role.insert(role_name=cur_role)
	    db.listing_role.insert(listing_ndx=listing_ndx,role_ndx=role_ndx)

	for cur_audio in audio.split(','):
	    audio_ndx = db(db.audio.path_to == cur_audio).select(db.audio.id).first()
	    if audio_ndx == None:
		audio_ndx = db.audio.insert(path_to=cur_audio)
	    db.listing_audio.insert(listing_ndx=listing_ndx,audio_ndx=audio_ndx)
	redirect(URL('listing',args=listing_ndx))
    elif form.errors:
	response.flash = 'errors' 

    return dict(form=form)

@auth.requires_login()
def auditionform():
    parent_ndx = request.args(0,cast=int)
    form = SQLFORM.factory(
		Field('desc','description', requires=IS_NOT_EMPTY()),
		Field('roles','Roles needed (Separated by commas)'),
		Field('genres','Genres (Separated by commas)'))
    if form.process().accepted:    
        desc = form.vars.desc
	genres = form.vars.genres
        roles = form.vars.roles
	audition_ndx = db.audition.insert(parent_ndx=parent_ndx,body=desc)
    
	for cur_genre in genres.split(','):
	    genre_ndx = db(db.genre.genre_name==cur_genre).select(db.genre.id).first()
	    if genre_ndx == None:
		genre_ndx = db.genre.insert(genre_name=cur_genre)
	    db.audition_genre.insert(audition_ndx=audition_ndx,genre_ndx=genre_ndx)
	'''
	for cur_role in roles.split(','):
	    role_ndx = db(db.role.role_name==cur_role).select(db.role.id).first()
	    if role_ndx == None:
		role_ndx = db.role.insert(role_name=role)
	    db.audition_role.insert(audition_ndx=audition_ndx,role_ndx=role_ndx)
	'''
	redirect(URL('audition', args=audition_ndx))
    elif form.errors:
	response.flash = 'errors' 

    return dict(form=form)

@auth.requires_login()
## All of a user's audio files
def audio():
    """
    SELECT *
    FROM AUDIO
    WHERE AUDIO.CREATED_BY = auth.user
    """
    return dict(form=auth())

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


