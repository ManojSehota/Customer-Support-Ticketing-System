from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Ticket, Message

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')


# -------------------- View all tickets --------------------
@tickets_bp.route('/')
@login_required
def list_tickets():
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('tickets/list.html', tickets=tickets)


# -------------------- Create a new ticket --------------------
@tickets_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        subject = request.form['subject']
        description = request.form['description']
        priority = request.form['priority']
        status = request.form['status']

        ticket = Ticket(subject=subject, description=description,
                        priority=priority, status=status, user_id=current_user.id)
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('tickets.list_tickets'))
    return render_template('tickets/create.html')


# -------------------- View / Reply to a ticket --------------------
@tickets_bp.route('/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    messages = Message.query.filter_by(ticket_id=ticket_id).order_by(Message.created_at.asc()).all()

    if request.method == 'POST':
        content = request.form['content']
        if content.strip():
            msg = Message(content=content, user_id=current_user.id, ticket_id=ticket.id)
            db.session.add(msg)
            db.session.commit()
            flash('Message added!', 'success')
        else:
            flash('Message cannot be empty.', 'warning')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

    return render_template('tickets/view.html', ticket=ticket, messages=messages)


# -------------------- Update Ticket --------------------
@tickets_bp.route('/update/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if request.method == 'POST':
        ticket.subject = request.form['subject']
        ticket.description = request.form['description']
        ticket.priority = request.form['priority']

        db.session.commit()
        flash('Ticket updated successfully!', 'info')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

    return render_template('tickets/update.html', ticket=ticket)


# -------------------- Delete Ticket --------------------
@tickets_bp.route('/delete/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket deleted successfully!', 'danger')
    return redirect(url_for('tickets.list_tickets'))
