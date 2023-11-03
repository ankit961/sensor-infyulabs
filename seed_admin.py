from flask.cli import AppGroup
from app import app, db
from model import User
import click
seed_admin_cli = AppGroup('seed_admin')

@seed_admin_cli.command('create')
def create_admin():
    """Seed the database with an admin user."""
    with app.app_context():
        # Check if the admin user already exists
        username= 'infyulabs'
        admin = User.query.filter_by(username=username).first()
        if admin:
            print('Admin user already exists.')
        else:
            admin = User(username=username, is_admin=True)
            admin.set_password("admin123")  # Use the set_password method on the instance
            db.session.add(admin)
            db.session.commit()
            print('Admin user seeded successfully.')

@seed_admin_cli.command('update_password')
@click.argument('username')
@click.argument('new_password')
def update_admin_password(username, new_password):
    """Update the password for an existing admin user."""
    with app.app_context():
        # Find the admin user by the provided username
        admin = User.query.filter_by(username=username).first()
        if admin:
            # Update the password using the set_password method
            admin.set_password(new_password)
            db.session.commit()
            print(f'Password for admin user {username} updated successfully.')
        else:
            print(f'Admin user {username} does not exist.')



# # # Import the User model
# # from app.models import User
# # @seed_admin_cli.command('update')
# # def update_admin():
# #     # Find the admin user by username or any other criteria
# #     admin_user = User.query.filter_by(username='admin').first()

# # # Check if the admin_user is found
# #     if admin_user:
# #     # Update the is_admin attribute to True
# #         admin_user.is_admin = True

# #     # Commit the changes to the database
# #         db.session.commit()
# #         print('Admin user updated successfully.')


# # Optionally, you can also handle the case where the admin user is not found
#     else:
#         print("Admin user not found in the database.")




if __name__ == '__main__':
    seed_admin_cli()
