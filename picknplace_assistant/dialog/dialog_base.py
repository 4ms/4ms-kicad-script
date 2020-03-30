# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainDialog
###########################################################################

class MainDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		#self.SetSizeHints( wx.Size( -1,250 ), wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Create PDF placement guide", wx.DefaultPosition, wx.Size( -1,-1 ), wx.ALIGN_CENTER_HORIZONTAL|wx.ST_NO_AUTORESIZE )
		self.m_staticText1.Wrap( 0 )

		self.m_staticText1.SetFont( wx.Font( 18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Lucida Grande" ) )

		bSizer1.Add( self.m_staticText1, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		m_radioBox1Choices = [ u"Both sides, combined PDFs", u"Front Only", u"Back Only" ]
		self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, u"Display components from:", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
		self.m_radioBox1.SetSelection( 0 )
		self.m_radioBox1.SetFont( wx.Font( 16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".Lucida Grande UI" ) )

		bSizer1.Add( self.m_radioBox1, 0, wx.ALL, 5 )

		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Path (relative to project):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		bSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.m_textPath = wx.TextCtrl( self, wx.ID_ANY, u"bom/", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_textPath, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer2.SetMinSize( wx.Size( -1,150 ) )
		self.m_button1 = wx.Button( self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.m_button1.SetDefault()
		self.m_button1.SetBitmapPosition( wx.LEFT )
		self.m_button1.SetBitmapMargins( wx.Size( 200,-1 ) )
		self.m_button1.SetFont( wx.Font( 12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer2.Add( self.m_button1, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button2 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.Point( -1,-1 ), wx.DefaultSize, 0 )

		self.m_button2.SetBitmapPosition( wx.RIGHT )
		self.m_button2.SetBitmapMargins( wx.Size( 200,-1 ) )
		self.m_button2.SetFont( wx.Font( 12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer2.Add( self.m_button2, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer2, 1, wx.ALIGN_CENTER_HORIZONTAL, 0 )


		self.SetSizer( bSizer1 )
		self.Layout()
		bSizer1.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.doCreatePDFs )
		self.m_button2.Bind( wx.EVT_BUTTON, self.doCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def doCreatePDFs( self, event ):
		event.Skip()

	def doCancel( self, event ):
		event.Skip()


