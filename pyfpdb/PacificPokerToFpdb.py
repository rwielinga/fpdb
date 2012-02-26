#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2008-2010, Carl Gherardi
#    
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
########################################################################

import L10n
_ = L10n.get_translation()

import sys
from HandHistoryConverter import *
from decimal_wrapper import Decimal

# PacificPoker HH Format

class PacificPoker(HandHistoryConverter):

    # Class Variables

    sitename = "PacificPoker"
    filetype = "text"
    codepage = ("utf8", "cp1252")
    siteId   = 13 # Needs to match id entry in Sites database

    mixes = { 'HORSE': 'horse', '8-Game': '8game', 'HOSE': 'hose'} # Legal mixed games
    sym = {'USD': "\$", 'CAD': "\$", 'T$': "", "EUR": "\xe2\x82\xac", "GBP": "\xa3", "play": ""}         # ADD Euro, Sterling, etc HERE
    substitutions = {
                     'LEGAL_ISO' : "USD|EUR|GBP|CAD|FPP",     # legal ISO currency codes
                            'LS' : u"\$|\xe2\x82\xac|\u20ac|" # legal currency symbols - Euro(cp1252, utf-8)
                    }
                    
    # translations from captured groups to fpdb info strings
    # not needed for PacificPoker
    #Lim_Blinds = {      '0.01': ('0.01', '0.02'),
    #                    '0.02': ('0.02', '0.04'),
    #                    '0.03': ('0.03', '0.06'),
    #                    '0.05': ('0.05', '0.10'),
    #                    '0.12': ('0.12', '0.25'),
    #                    '0.25': ('0.25', '0.50'),
    #                    '0.50': ('0.50', '1.00'),
    #                    '1.00': ('1.00', '2.00'),         '1': ('1.00', '2.00'),
    #                    '2.00': ('2.00', '4.00'),         '2': ('2.00', '4.00'),
    #                    '3.00': ('3.00', '6.00'),         '3': ('3.00', '6.00'),
    #                    '5.00': ('5.00', '10.00'),        '5': ('5.00', '10.00'),
    #                   '10.00': ('10.00', '20.00'),      '10': ('10.00', '20.00'),
    #                   '15.00': ('15.00', '30.00'),      '15': ('15.00', '30.00'),
    #                   '30.00': ('30.00', '60.00'),      '30': ('30.00', '60.00'),
    #                   '50.00': ('50.00', '100.00'),     '50': ('50.00', '100.00'),
    #                   '75.00': ('75.00', '150.00'),     '75': ('75.00', '150.00'),
    #                  '100.00': ('100.00', '200.00'),   '100': ('100.00', '200.00'),
    #                  '200.00': ('200.00', '400.00'),   '200': ('200.00', '400.00'),
    #                  '250.00': ('250.00', '500.00'),   '250': ('250.00', '500.00')
    #              }

    limits = { 'No Limit':'nl', 'Pot Limit':'pl', 'Limit':'fl', 'LIMIT':'fl', 'Fix Limit':'fl' }

    games = {                          # base, category
                             "Hold'em"  : ('hold','holdem'),
                               'Holdem' : ('hold','holdem'),
                                'Omaha' : ('hold','omahahi'),
                          'Omaha Hi/Lo' : ('hold','omahahilo'),
                              'OmahaHL' : ('hold','omahahilo'),
                                 'Razz' : ('stud','razz'), 
                                 'RAZZ' : ('stud','razz'),
                          '7 Card Stud' : ('stud','studhi'),
                    '7 Card Stud Hi/Lo' : ('stud','studhilo'),
                               'Badugi' : ('draw','badugi'),
              'Triple Draw 2-7 Lowball' : ('draw','27_3draw'),
              'Single Draw 2-7 Lowball' : ('draw','27_1draw'),
                          '5 Card Draw' : ('draw','fivedraw')
               }

    currencies = { u'€':'EUR', '$':'USD', '':'T$' }

    # Static regexes
    re_GameInfo     = re.compile(u"""
          (\#Game\sNo\s:\s[0-9]+\\n)?
          \*\*\*\*\*\sCassava\sHand\sHistory\sfor\sGame\s(?P<HID>[0-9]+)\s\*\*\*\*\*\\n
          (?P<CURRENCY>%(LS)s)?(?P<SB>[.,0-9]+)/(%(LS)s)?(?P<BB>[.,0-9]+)\sBlinds\s
          (?P<LIMIT>No\sLimit|Fix\sLimit|Pot\sLimit)\s
          (?P<GAME>Holdem|Omaha|OmahaHL|Hold\'em|Omaha\sHi/Lo|OmahaHL|Razz|RAZZ|7\sCard\sStud|7\sCard\sStud\sHi/Lo|Badugi|Triple\sDraw\s2\-7\sLowball|Single\sDraw\s2\-7\sLowball|5\sCard\sDraw)
          \s-\s\*\*\*\s
          (?P<DATETIME>.*$)\s
          (Tournament\s\#(?P<TOURNO>\d+))?
          """ % substitutions, re.MULTILINE|re.VERBOSE)

    re_PlayerInfo   = re.compile(u"""
          ^Seat\s(?P<SEAT>[0-9]+):\s
          (?P<PNAME>.*)\s
          \(\s(%(LS)s)?(?P<CASH>[.,0-9]+)\s\)""" % substitutions, 
          re.MULTILINE|re.VERBOSE)

    re_HandInfo     = re.compile("""
          ^(
            (Table\s(?P<TABLE>[-\ \#a-zA-Z\d]+)\s)
            |
            (Tournament\s\#(?P<TOURNO>\d+)\s
                (?P<BUYIN>(
                  ((?P<BIAMT>[%(LS)s\d\.]+)?\s\+\s?(?P<BIRAKE>[%(LS)s\d\.]+))
                  |(Free)
                ))\s-\s
                Table\s\#(?P<TABLENO>\d+)\s
            )
           )
          (\(Real\sMoney\))?
          (?P<PLAY>\(Practice\sPlay\))?
          \\n
          Seat\s(?P<BUTTON>[0-9]+)\sis\sthe\sbutton
          """ % substitutions, re.MULTILINE|re.VERBOSE)

    re_SplitHands   = re.compile('\n\n+')
    re_TailSplitHands   = re.compile('(\n\n\n+)')
    re_Button       = re.compile('Seat (?P<BUTTON>\d+) is the button', re.MULTILINE)
    re_Board        = re.compile(r"\[\s(?P<CARDS>.+)\s\]")

    re_DateTime     = re.compile("""(?P<D>[0-9]{2})\s(?P<M>[0-9]{2})\s(?P<Y>[0-9]{4})[\- ]+(?P<H>[0-9]+):(?P<MIN>[0-9]+):(?P<S>[0-9]+)""", re.MULTILINE)

    short_subst = {'PLYR': r'(?P<PNAME>.+?)', 'CUR': '\$?'}
    re_PostSB           = re.compile(r"^%(PLYR)s posts small blind \[%(CUR)s(?P<SB>[.,0-9]+)\]" %  short_subst, re.MULTILINE)
    re_PostBB           = re.compile(r"^%(PLYR)s posts big blind \[%(CUR)s(?P<BB>[.,0-9]+)\]" %  short_subst, re.MULTILINE)
    re_Antes            = re.compile(r"^%(PLYR)s posts the ante \[%(CUR)s(?P<ANTE>[.,0-9]+)\]" % short_subst, re.MULTILINE)
    # TODO: unknown in available hand histories for pacificpoker:
    re_BringIn          = re.compile(r"^%(PLYR)s: brings[- ]in( low|) for %(CUR)s(?P<BRINGIN>[.,0-9]+)" % short_subst, re.MULTILINE)
    re_PostBoth         = re.compile(r"^%(PLYR)s posts dead blind \[%(CUR)s(?P<SBBB>[.,0-9]+)\s\+\s%(CUR)s[.,0-9]+\]" %  short_subst, re.MULTILINE)
    re_HeroCards        = re.compile(r"^Dealt to %(PLYR)s( \[\s(?P<NEWCARDS>.+?)\s\])" % short_subst, re.MULTILINE)
    re_Action           = re.compile(r"""
                        ^%(PLYR)s(?P<ATYPE>\sbets|\schecks|\sraises|\scalls|\sfolds|\sdiscards|\sstands\spat)
                        (\s\[(%(CUR)s)?(?P<BET>[.,0-9]+)\])?
                        (\s*and\sis\sall.in)?
                        (\s*and\shas\sreached\sthe\s[%(CUR)s\d\.]+\scap)?
                        (\s*cards?(\s\[(?P<DISCARDED>.+?)\])?)?\s*$"""
                         %  short_subst, re.MULTILINE|re.VERBOSE)
    re_ShowdownAction   = re.compile(r"^%s shows \[(?P<CARDS>.*)\]" % short_subst['PLYR'], re.MULTILINE)
    re_sitsOut          = re.compile("^%s sits out" %  short_subst['PLYR'], re.MULTILINE)
    re_ShownCards       = re.compile("^%s ?(?P<SHOWED>shows|mucks) \[ (?P<CARDS>.*) \]$" %  short_subst['PLYR'], re.MULTILINE)
    re_CollectPot       = re.compile(r"^%(PLYR)s collected \[ %(CUR)s(?P<POT>[.,0-9]+) \]$" %  short_subst, re.MULTILINE)

    def compilePlayerRegexs(self,  hand):
        pass

    def readSupportedGames(self):
        return [["ring", "hold", "nl"],
                ["ring", "hold", "pl"],
                ["ring", "hold", "fl"],

                ["ring", "stud", "fl"],

                ["ring", "draw", "fl"],
                ["ring", "draw", "pl"],
                ["ring", "draw", "nl"],

                ["tour", "hold", "nl"],
                ["tour", "hold", "pl"],
                ["tour", "hold", "fl"],

                ["tour", "stud", "fl"],
                
                ["tour", "draw", "fl"],
                ["tour", "draw", "pl"],
                ["tour", "draw", "nl"],
                ]

    def determineGameType(self, handText):
        info = {}
        m = self.re_GameInfo.search(handText)
        if not m:
            tmp = handText[0:200]
            log.error(_("PacificPokerToFpdb.determineGameType: '%s'") % tmp)
            raise FpdbParseError

        mg = m.groupdict()
        #print "DEBUG: mg: ", mg
        if 'LIMIT' in mg:
            #print "DEBUG: re_GameInfo[LIMIT] \'", mg['LIMIT'], "\'"
            info['limitType'] = self.limits[mg['LIMIT']]
        if 'GAME' in mg:
            #print "DEBUG: re_GameInfo[GAME] \'", mg['GAME'], "\'"
            (info['base'], info['category']) = self.games[mg['GAME']]
        if 'SB' in mg:
            #print "DEBUG: re_GameInfo[SB] \'", mg['SB'], "\'"
            info['sb'] = self.clearMoneyString(mg['SB'])
        if 'BB' in mg:
            #print "DEBUG: re_GameInfo[BB] \'", mg['BB'], "\'"
            info['bb'] = self.clearMoneyString(mg['BB'])
        if 'CURRENCY' in mg:
            #print "DEBUG: re_GameInfo[CURRENCY] \'", mg['CURRENCY'], "\'"
            info['currency'] = self.currencies[mg['CURRENCY']]

        if 'TOURNO' in mg and mg['TOURNO'] is not None:
            info['type'] = 'tour'
        else:
            info['type'] = 'ring'

        # Pacific Poker includes the blind levels in the gametype, the following is not needed.
        #if info['limitType'] == 'fl' and info['bb'] is not None and info['type'] == 'ring' and info['base'] != 'stud':
        #    try:
        #        info['sb'] = self.Lim_Blinds[mg['BB']][0]
        #        info['bb'] = self.Lim_Blinds[mg['BB']][1]
        #    except KeyError:
        #        log.error(_("determineGameType: Lim_Blinds has no lookup for '%s'" % mg['BB']))
        #        log.error(_("determineGameType: Raising FpdbParseError"))
        #        raise FpdbParseError(_("Lim_Blinds has no lookup for '%s'") % mg['BB'])

        return info

    def readHandInfo(self, hand):
        info = {}
        m  = self.re_HandInfo.search(hand.handText,re.DOTALL)
        m2 = self.re_GameInfo.search(hand.handText)
        if m is None or m2 is None:
            tmp = hand.handText[0:200]
            log.error(_("PacificPokerToFpdb.readHandInfo: '%s'") % tmp)
            if m is None:
                log.error("PacificPokerToFpdb.readHandInfo: re_HandInfo could not be parsed")
            if m2 is None:
                log.error("PacificPokerToFpdb.readHandInfo: re_GameInfo could not be parsed")
            raise FpdbParseError

        info.update(m.groupdict())
        info.update(m2.groupdict())

        #log.debug("readHandInfo: %s" % info)
        for key in info:
            log.debug("hand.tablename==%s." % hand.tablename)
            if key == 'DATETIME':
                # 28 11 2011 19:05:11
                m1 = self.re_DateTime.finditer(info[key])
                datetimestr = "2000/01/01 00:00:00"  # default used if time not found
                for a in m1:
                    datetimestr = "%s/%s/%s %s:%s:%s" % (a.group('Y'), a.group('M'),a.group('D'),a.group('H'),a.group('MIN'),a.group('S'))
                hand.startTime = datetime.datetime.strptime(datetimestr, "%Y/%m/%d %H:%M:%S")
                hand.startTime = HandHistoryConverter.changeTimezone(hand.startTime, "ET", "UTC")
            if key == 'HID':
                hand.handid = info[key]
            if key == 'TABLE' and info[key] != None:
                hand.tablename = info[key]
            if key == 'TABLENO' and info[key] != None:
                # Table number for tournaments. Either TABLE or TABLENO should be filled in re_HandInfo
                hand.tablename = info[key]
            if key == 'TOURNO':
                hand.tourNo = info[key]
            if key == 'BUYIN' and info['BUYIN'] != None:
                if info[key] == 'Free':
                    hand.buyin = 0
                    hand.fee = 0
                    if 'CURRENCY' in info and info['CURRENCY'] == "$":
                        hand.buyinCurrency = "USD"
                    else:
                        hand.buyinCurrency = "FREE"
                else:
                    if info[key].find("$")!=-1:
                        hand.buyinCurrency="USD"
                    if 'PLAY' in info and info['PLAY'] != "Practice Play":
                        hand.buyinCurrency="FREE"
                    else:
                        #FIXME: handle other currencies, FPP, play money
                        log.error(_("PacificPokerToFpdb.readHandInfo: Failed to detect currency.") + " Hand ID: %s: '%s'" % (hand.handid, info[key]))
                        raise FpdbParseError

                    info['BIAMT'] = info['BIAMT'].strip(u'$€')
                    info['BIRAKE'] = info['BIRAKE'].strip(u'$€')

                    hand.buyin = int(100*Decimal(info['BIAMT']))
                    hand.fee = int(100*Decimal(info['BIRAKE']))

            if key == 'TABLE' and info['TABLE'] != None:
                hand.tablename = info[key]
            if key == 'TABLEID' and info['TABLEID'] != None:
                hand.tablename = info[key]
            if key == 'BUTTON':
                hand.buttonpos = info[key]

            if key == 'PLAY' and info['PLAY'] is not None:
                #hand.currency = 'play' # overrides previously set value
                hand.gametype['currency'] = 'play'
    
    def readButton(self, hand):
        m = self.re_Button.search(hand.handText)
        if m:
            hand.buttonpos = int(m.group('BUTTON'))
        else:
            log.info('readButton: ' + _('not found'))

    def readPlayerStacks(self, hand):
        m = self.re_PlayerInfo.finditer(hand.handText)
        for a in m:
            #print "DEBUG: Seat[", a.group('SEAT'), "]; PNAME[", a.group('PNAME'), "]; CASH[", a.group('CASH'), "]"
            hand.addPlayer(int(a.group('SEAT')), a.group('PNAME'), a.group('CASH'))

    def markStreets(self, hand):
        # PREFLOP = ** Dealing down cards **
        # This re fails if,  say, river is missing; then we don't get the ** that starts the river.
        if hand.gametype['base'] in ("hold"):
            m =  re.search(r"\*\* Dealing down cards \*\*(?P<PREFLOP>.+(?=\*\* Dealing flop \*\*)|.+)"
                       r"(\*\* Dealing flop \*\* (?P<FLOP>\[ \S\S, \S\S, \S\S \].+(?=\*\* Dealing turn \*\*)|.+))?"
                       r"(\*\* Dealing turn \*\* (?P<TURN>\[ \S\S \].+(?=\*\* Dealing river \*\*)|.+))?"
                       r"(\*\* Dealing river \*\* (?P<RIVER>\[ \S\S \].+?(?=\*\* Summary \*\*)|.+))?"
                       , hand.handText,re.DOTALL)
        if m is None:
            log.error(_("PacificPokerToFpdb.markStreets: Unable to recognise streets"))
            raise FpdbParseError
        else:
            #print "DEBUG: Matched markStreets"
            mg = m.groupdict()
#            if 'PREFLOP' in mg:
#                print "DEBUG: PREFLOP: ", [mg['PREFLOP']]
#            if 'FLOP' in mg:
#                print "DEBUG: FLOP: ", [mg['FLOP']]
#            if 'TURN' in mg:
#                print "DEBUG: TURN: ", [mg['TURN']]
#            if 'RIVER' in mg:
#                print "DEBUG: RIVER: ", [mg['RIVER']]

        hand.addStreets(m)

    def readCommunityCards(self, hand, street): # street has been matched by markStreets, so exists in this hand
        if street in ('FLOP','TURN','RIVER'):   # a list of streets which get dealt community cards (i.e. all but PREFLOP)
            #print "DEBUG readCommunityCards:", street, hand.streets.group(street)
            m = self.re_Board.search(hand.streets[street])
            hand.setCommunityCards(street, m.group('CARDS').split(', '))

    def readAntes(self, hand):
        m = self.re_Antes.finditer(hand.handText)
        for player in m:
            #~ logging.debug("hand.addAnte(%s,%s)" %(player.group('PNAME'), player.group('ANTE')))
            hand.addAnte(player.group('PNAME'), player.group('ANTE'))
    
    def readBringIn(self, hand):
        m = self.re_BringIn.search(hand.handText,re.DOTALL)
        if m:
            #~ logging.debug("readBringIn: %s for %s" %(m.group('PNAME'),  m.group('BRINGIN')))
            hand.addBringIn(m.group('PNAME'),  m.group('BRINGIN'))
        
    def readBlinds(self, hand):
        liveBlind = True
        for a in self.re_PostSB.finditer(hand.handText):
            if a.group('PNAME') in hand.stacks:
                if liveBlind:
                    hand.addBlind(a.group('PNAME'), 'small blind', a.group('SB'))
                    liveBlind = False
                else:
                    # Post dead blinds as ante
                    hand.addBlind(a.group('PNAME'), 'secondsb', a.group('SB'))
            else:
                raise FpdbHandPartial("Partial hand history: %s" % hand.handid)
        for a in self.re_PostBB.finditer(hand.handText):
            if a.group('PNAME') in hand.stacks:
                hand.addBlind(a.group('PNAME'), 'big blind', a.group('BB'))
            else:
                raise FpdbHandPartial("Partial hand history: %s" % hand.handid)
        for a in self.re_PostBoth.finditer(hand.handText):
            if a.group('PNAME') in hand.stacks:
                hand.addBlind(a.group('PNAME'), 'both', a.group('SBBB'))
            else:
                raise FpdbHandPartial("Partial hand history: %s" % hand.handid)

    def readHeroCards(self, hand):
#    streets PREFLOP, PREDRAW, and THIRD are special cases beacause
#    we need to grab hero's cards
        for street in ('PREFLOP', 'DEAL'):
            if street in hand.streets.keys():
                m = self.re_HeroCards.finditer(hand.streets[street])
                for found in m:
#                    if m == None:
#                        hand.involved = False
#                    else:
                    hand.hero = found.group('PNAME')
                    newcards = found.group('NEWCARDS').split(', ')
                    hand.addHoleCards(street, hand.hero, closed=newcards, shown=False, mucked=False, dealt=True)

        for street, text in hand.streets.iteritems():
            if not text or street in ('PREFLOP', 'DEAL'): continue  # already done these
            m = self.re_HeroCards.finditer(hand.streets[street])
            for found in m:
                player = found.group('PNAME')
                if found.group('NEWCARDS') is None:
                    newcards = []
                else:
                    newcards = found.group('NEWCARDS').split(', ')
                if found.group('OLDCARDS') is None:
                    oldcards = []
                else:
                    oldcards = found.group('OLDCARDS').split(', ')

                if street == 'THIRD' and len(newcards) == 3: # hero in stud game
                    hand.hero = player
                    hand.dealt.add(player) # need this for stud??
                    hand.addHoleCards(street, player, closed=newcards[0:2], open=[newcards[2]], shown=False, mucked=False, dealt=False)
                else:
                    hand.addHoleCards(street, player, open=newcards, closed=oldcards, shown=False, mucked=False, dealt=False)


    def readAction(self, hand, street):
        m = self.re_Action.finditer(hand.streets[street])
        for action in m:
            acts = action.groupdict()
            #print "DEBUG: acts: %s" %acts
            if action.group('PNAME') in hand.stacks:
                if action.group('ATYPE') == ' folds':
                    hand.addFold( street, action.group('PNAME'))
                elif action.group('ATYPE') == ' checks':
                    hand.addCheck( street, action.group('PNAME'))
                elif action.group('ATYPE') == ' calls':
                    hand.addCall( street, action.group('PNAME'), action.group('BET').replace(',','') )
                elif action.group('ATYPE') == ' raises':
                    hand.addCallandRaise( street, action.group('PNAME'), action.group('BET').replace(',','') )
                elif action.group('ATYPE') == ' bets':
                    hand.addBet( street, action.group('PNAME'), action.group('BET').replace(',','') )
                elif action.group('ATYPE') == ' discards':
                    hand.addDiscard(street, action.group('PNAME'), action.group('BET').replace(',',''), action.group('DISCARDED'))
                elif action.group('ATYPE') == ' stands pat':
                    hand.addStandsPat( street, action.group('PNAME'))
                else:
                    print (_("DEBUG:") + " " + _("Unimplemented %s: '%s' '%s'") % ("readAction", action.group('PNAME'), action.group('ATYPE')))
            else:
                raise FpdbHandPartial("Partial hand history: '%s', '%s' not in hand.stacks" % (hand.handid, action.group('PNAME')))
            

    def readShowdownActions(self, hand):
        # TODO: pick up mucks also??
        for shows in self.re_ShowdownAction.finditer(hand.handText):            
            cards = shows.group('CARDS').split(', ')
            hand.addShownCards(cards, shows.group('PNAME'))

    def readCollectPot(self,hand):
        for m in self.re_CollectPot.finditer(hand.handText):
            #print "DEBUG: hand.addCollectPot(player=", m.group('PNAME'), ", pot=", m.group('POT'), ")"
            hand.addCollectPot(player=m.group('PNAME'),pot=m.group('POT').replace(',',''))

    def readShownCards(self,hand):
        for m in self.re_ShownCards.finditer(hand.handText):
            if m.group('CARDS') is not None:
                cards = m.group('CARDS')
                cards = cards.split(', ') # needs to be a list, not a set--stud needs the order

                (shown, mucked) = (False, False)
                if m.group('SHOWED') == "showed": shown = True
                elif m.group('SHOWED') == "mucked": mucked = True

                #print "DEBUG: hand.addShownCards(%s, %s, %s, %s)" %(cards, m.group('PNAME'), shown, mucked)
                hand.addShownCards(cards=cards, player=m.group('PNAME'), shown=shown, mucked=mucked)

    @staticmethod
    def getTableTitleRe(type, table_name=None, tournament = None, table_number=None):
        # Tournament tables look like:
        # Tour NLH 50+5 Brouhaha ID #28353026 Table #7 Blinds: 200/400
        log.info("Pacific.getTableTitleRe: table_name='%s' tournament='%s' table_number='%s'" % (table_name, tournament, table_number))
        regex = "%s" % (table_name)
        if tournament:
            regex = "%s Table #%s" % (tournament, table_number)

        log.info("Pacific.getTableTitleRe: returns: '%s'" % (regex))
        return regex
