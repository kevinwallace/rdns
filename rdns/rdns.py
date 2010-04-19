import zope.interface

from twisted.internet import defer, reactor
from twisted.names import client, dns

from IPy import IP


class RecurseLimitExceeded(Exception):
    pass


class GatedDeferredFunction(object):
    """
    I wrap a function, and only allow a certain number of calls to that function to be outstanding
    at any given moment.  Any additional calls are queued and sent in a FIFO order.
    """
    
    def __init__(self, func, maxInFlight):
        self.func = func
        self.maxInFlight = maxInFlight
        self.inFlight = 0
        self.calls = []
    
    def __call__(self, *args, **kwargs):
        d = defer.Deferred()
        self.calls.append((d, args, kwargs))
        self.__sendOutstanding()
        return d
    
    def __sendOutstanding(self):
        def gotOne(val):
            self.inFlight -= 1
            reactor.callLater(0, self.__sendOutstanding)
            return val
        
        while self.inFlight < self.maxInFlight and self.calls:
            self.inFlight += 1
            d, args, kwargs = self.calls.pop(0)
            defer.maybeDeferred(self.func, *args, **kwargs).addBoth(gotOne).chainDeferred(d)


def _getRecordsForName(answers, name):
    records = []
    for answer in answers:
        if answer.name.name.rstrip('.') == name.rstrip('.'):
            if answer.payload.TYPE == dns.CNAME:
                cnameRecords = _getRecordsForName(answers, answer.payload.name.name)
                if cnameRecords:
                    records.extend(cnameRecords)
                else:
                    records.append(answer.payload)
            else:
                records.append(answer.payload)
    return records


def _recursiveLookup(reverseName, lookupFunc, depth=0, maxRecurseDepth=10):
    if depth >= maxRecurseDepth:
        return defer.fail(RecurseLimitExceeded())
    else:
        @defer.inlineCallbacks
        def gotResult((answers, auth, add)):
            resolved = []
            for record in _getRecordsForName(answers, reverseName):
                if record.TYPE == dns.CNAME:
                    result = yield _recursiveLookup(record.name.name, lookupFunc, depth + 1, maxRecurseDepth)
                    resolved.extend(result)
                else:
                    resolved.append(defer.succeed(record))
            
            records = []
            for result in resolved:
                record = yield result
                records.append(record)
            defer.returnValue(records)
        
        def gotError(error):
            # eat DomainErrors - they just signify that there's no result
            if not isinstance(error.value, dns.DomainError):
                return error
            return []
        
        return lookupFunc(reverseName).addCallbacks(gotResult, gotError)


def resolveAs(name, maxInFlight=200, maxRecurseDepth=10, resolver=client):
    lookupPointer = GatedDeferredFunction(resolver.lookupAddress, maxInFlight)
    def getAddresses(records):
        return [record.dottedQuad() for record in records]
    return _recursiveLookup(name, lookupFunc=lookupPointer, maxRecurseDepth=maxRecurseDepth).addCallback(getAddresses)


def resolvePTRs(ips, maxInFlight=200, maxRecurseDepth=10, resolver=client):
    lookupPointer = GatedDeferredFunction(resolver.lookupPointer, maxInFlight)
    def getNames(records):
        return [record.name.name for record in records]
    return [(ip, _recursiveLookup(ip.reverseName(), lookupFunc=lookupPointer, maxRecurseDepth=maxRecurseDepth).addCallback(getNames)) for ip in ips]
