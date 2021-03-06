import wx
import qy.graphics
from qy.analysis.coincidence_counting import parse_coincidence_pattern
import qy.settings
import beeper


class browser_block(wx.Panel):

    def __init__(self, parent, index):
        ''' An input/output pair '''
        wx.Panel.__init__(self, parent)
        self.index = index
        self.colour = qy.graphics.colors.get_pastel_rgb(index)
        self.SetBackgroundColour(self.colour)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_box = wx.TextCtrl(self)
        self.input_box.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.output_box = wx.StaticText(self, label='--',
                                        style=wx.ST_NO_AUTORESIZE | wx.ALIGN_RIGHT | wx.SIMPLE_BORDER)
        self.output_box.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.input_box, 0, wx.RIGHT | wx.LEFT, 0)
        sizer.Add(self.output_box, 1, wx.EXPAND | wx.RIGHT | wx.LEFT, 0)
        self.SetSizerAndFit(sizer)
        self.Fit()

    def bind(self, function):
        ''' Call a function evey time the user types something '''
        self.input_box.Bind(wx.EVT_TEXT, function)

    def set_input(self, value):
        ''' Set the search term '''
        self.input_box.SetValue(value)

    def set_output(self, value):
        ''' Set the output value '''
        try:
            self.output_box.SetLabel('{:,}'.format(value))
        except ValueError:
            self.output_box.SetLabel('')

    def get_input(self):
        ''' Get the current search '''
        return self.input_box.GetValue().encode('ascii', 'ignore')


class browser(wx.Panel):

    ''' A wx GUI component to efficiently look at many count rates '''

    def __init__(self, parent, number=16):
        ''' Constructor '''
        wx.Panel.__init__(self, parent)
        self.number = number
        self.beep = qy.settings.get('realtime.sound')
        self.build()

    def build(self):
        ''' Build the widget '''
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.blocks = []
        for i in range(self.number):
            block = browser_block(parent=self, index=i)
            # block.bind(self.patterns_changed)
            self.blocks.append(block)
            mainsizer.Add(block, 0, wx.TOP | wx.EXPAND, border=0)

        self.SetSizerAndFit(mainsizer)

    def set_patterns(self, patterns):
        ''' Set all of the patterns (inputs) at once'''
        for i in range(min(len(patterns), len(self.blocks))):
            self.blocks[i].set_input(patterns[i])

    def get_patterns(self):
        ''' Get all of the patterns as text '''
        return [b.get_input() for b in self.blocks]

    def toggle_beep(self, event):
        ''' Toggle hi-contrast mode '''
        self.beep = event.GetEventObject().IsChecked()

    def update_count_rates(self, count_rates):
        '''
        The postprocessing system sent us new count rates.
        Process them, and forward the filtered counts onto the graph
        '''

        filtered_count_rates = []

        for block in self.blocks:
            pattern = block.get_input().strip()
            if len(pattern) > 0:
                value = parse_coincidence_pattern(pattern, count_rates)
                block.set_output(value)
                filtered_count_rates.append({'pattern': pattern,
                                             'count': value, 'index': block.index})
            else:
                block.set_output(None)

        if self.beep and len(filtered_count_rates) > 0:
            beeper.beep(filtered_count_rates[0]['count'])

        return filtered_count_rates
