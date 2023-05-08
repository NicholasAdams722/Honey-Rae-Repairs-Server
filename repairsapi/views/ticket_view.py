"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket
from repairsapi.models import Employee
from repairsapi.models import Customer



class TicketView(ViewSet):
    """Honey Rae API tickets view"""

    def update(self, request, pk=None):
        """Handle PUT requests for single customer
        
        Returns:
            Response -- No response body. Just 204 status code.
        """

        # Select the targeted ticket using pk
        ticket = ServiceTicket.objects.get(pk=pk)

        # Get the employee id from the client request
        employee_id = request.data["employee"]

        #Select the employee from the database using that id 
        assigned_employee = Employee.objects.get(pk=employee_id)

        # Assign that employee instance to the employee property of the ticket
        ticket.employee = assigned_employee

        #save the updated ticket
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT) 

    def create(self, request):
        """Handle POST request for service tickets
        Returns: 
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data["description"]
        new_ticket.emergency = request.data["emergency"]
        new_ticket.save()

        serialized = TicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for service tickets
        
        Returns:
            Response: None with 204 status code
        """
        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """Handle GET requests to get all tickets

        Returns:
            Response -- JSON serialized list of tickets
        """
        service_tickets = []
        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()
            
        if "status" in request.query_params:
            if request.query_params['status'] == "done":
                service_tickets = service_tickets.filter(date_completed__isnull=False)



        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = TicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single ticket

        Returns:
            Response -- JSON serialized ticket record
        """

        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(ticket)
        return Response(serialized.data, status=status.HTTP_200_OK)

class TicketEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')

class TicketCustomerSerializer(serializers.ModelSerializer):

    class Meta: 
        model= Customer 
        fields = ('id', 'address', 'full_name')

class TicketSerializer(serializers.ModelSerializer):
    """JSON serializer for tickets"""
    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)
    class Meta:
        model = ServiceTicket
        fields = ( 'id', 'description', 'emergency', 'date_completed', 'employee', 'customer', )
        depth = 1
        #Depth expands all foreign keys