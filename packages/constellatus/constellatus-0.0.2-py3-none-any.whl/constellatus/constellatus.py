import eons
import inspect
from apie import APIE
from flask import request
from flask import Response

######## START CONTENT ########

class CONSTELLATUS(APIE):
	def __init__(this, name="Constellatus", description="Stars for Eons"):
		super().__init__(name, description)

		this.optionalKWArgs['port'] = 1137
		
	# Acquire and run the given endpoint with the given request.
	def ProcessEndpoint(this, endpointName, request, **kwargs):
		if (':' not in endpointName):
			return super().ProcessEndpoint(endpointName, request, **kwargs)
		
		star = this.Observe(endpointName)
		if (not star):
			return Response(
				status=404,
				response=f"Could not find {endpointName}",
				mimetype='text/plain'
			)
		
		starSourceFile = getattr(inspect.getmodule(type(star)), '_source')
		starData = ""
		with open(starSourceFile, 'r') as starSource:
			starData = starSource.read()
		return Response(
			response = starData,
			mimetype = 'text/plain',
			content_type = 'text/plain',
			direct_passthrough = True,
			status = 200
		)

	def Observe(this, cluster):
		if (cluster.startswith('::')):
			cluster = cluster[2:]
		elif(cluster.startswith(':')):
			cluster = cluster[1:]
		
		namespaceString = ':'.join(cluster.split(':')[:-1])
		packageName = cluster.split(':')[-1]
		packageType = ""
		if ('.' in packageName):
			packageType = packageName.split('.')[-1]
			packageName = '.'.join(packageName.split('.')[:-1])
		
		star = None
		try:
			star = this.GetRegistered(packageName, packageType, namespaceString)
		except:
			pass
		
		return star

	def Collapse(this, cloud):
		cloudFragments = []
		pass

	def Condense(this, cloudFragment):
		protostar = None
		return protostar

	def Ignite(this, protostar):
		star = protostar
		return star
	
	def Destroy(this, star):
		pass
