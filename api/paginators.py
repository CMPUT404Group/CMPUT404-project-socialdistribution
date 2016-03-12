from rest_framework import pagination
from rest_framework.response import Response
from rest_framework import status

'''
Handles the pagination of posts for the API
'''
class ListPaginator(pagination.PageNumberPagination):
	page_size = 15
	page_size_query_param = 'size'
	max_page_size = 50

	def get_paginated_response(self, data):
		if self.request.GET.get("size") != None:
			size = int(self.request.GET.get("size"))
		else:
			size = self.page_size

		return Response({
			'query': data['query'],
			'count': self.page.paginator.count,
			'size': size,
			'next': self.get_next_link(),
			'previous': self.get_previous_link(),
			data['query']: data['data'],
		}, status=status.HTTP_200_OK)
