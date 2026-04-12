from app import app, controllers


app.add_url_rule('/', 'index', controllers.index)

if __name__ == '__main__':
    app.run(debug=True)