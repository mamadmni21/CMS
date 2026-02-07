from app import create_app

# Vercel looks for the variable 'app'
app = create_app()

# You don't technically need the __main__ block for Vercel, 
# but keeping it allows you to still run it locally via 'python app.py'
if __name__ == "__main__":
    app.run(debug=True)