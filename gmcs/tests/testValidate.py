#!/bin/usr/env python2.7
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from gmcs.choices import ChoicesFile
from gmcs.validate import validate


class TestValidate(unittest.TestCase):

  ## Methods for asserting the presence of errors and warnings when
  ## a ChoicesFile is put through validation

  def assertErrorsOrWarnings(self, c, variables, errors):
    vr = validate(c)
    d = vr.errors if errors else vr.warnings
    for v in variables:
      self.assertTrue(v in d, "Missing %s for variable named %s" % ('error' if errors else 'warning', v))


  def assertWarning(self, c, warning):
    self.assertErrorsOrWarnings(c, (warning,), False)


  def assertWarnings(self, c, warnings):
    self.assertErrorsOrWarnings(c, warnings, False)


  def assertError(self, c, error):
    self.assertErrorsOrWarnings(c, (error,), True)


  def assertErrors(self, c, errors):
    self.assertErrorsOrWarnings(c, errors, True)


  def assertNoErrorsOrWarnings(self, c, variables, errors):
    vr = validate(c)
    d = vr.errors if errors else vr.warnings
    for v in variables:
      self.assertFalse(v in d, "Variable named %s trigged unexpected error: \"%s\"" % (v, (u"" if v not in d else d[v].message)))


  def assertNoWarning(self, c, warning):
    self.assertNoErrorsOrWarnings(c, (warning,), False)


  def assertNoWarnings(self, c, warnings):
    self.assertNoErrorsOrWarnings(c, warnings, False)


  def assertNoError(self, c, error):
    self.assertNoErrorsOrWarnings(c, (error,), True)


  def assertNoErrors(self, c, errors):
    self.assertNoErrorsOrWarnings(c, errors, True)


class TestBasic(TestValidate):

  def test_names(self):
    # Pairs of [variable prefix, value suffix].  Appending 'name' to the
    # prefix gives the variable name (e.g., 'case1_name').  The suffix
    # tells what the system will append to the end of the *value* of
    # that variable.
    variables = (['nom-acc-nom-case-', ''],
                 ['case1_', ''],
                 ['number1_', ''],
                 ['gender1_', ''],
                 ['feature1_', ''],
                 ['feature1_value1_', ''],
                 ['tense1_', ''],
                 ['aspect1_', ''],
                 ['situation1_', ''],
                 ['nf-subform1_', ''],
                 ['fin-subform1_', ''],
                 ['noun1_', '-noun-lex'],
                 ['noun2_', '-noun-lex'],
                 ['det1_', '-determiner-lex'],
                 ['det2_', '-determiner-lex'],
                 ['verb1_', '-verb-lex'],
                 ['verb2_', '-verb-lex'],
                 ['noun-pc1_', '-lex-rule'],
                 ['noun-pc1_lrt1_', '-lex-rule'],
                 ['noun-pc2_', '-lex-rule'],
                 ['noun-pc2_lrt1_', '-lex-rule'])

    # Name for causing collisions, made up of the lower-case letter 'a' in:
    #   Latin, accented Latin, accented Latin, Greek, Cyrillic, Armenian
    value = u'aáāαаա'

    for v1 in variables:
      # first try colliding with an existing name (head-comp-phrase)
      if not v1[1]:  # won't collide if there's a suffix
        name = v1[0] + 'name'
        c = ChoicesFile()
        c[name] = 'head-comp-phrase'
        self.assertError(c, name)

      # next try colliding pairs of names
      for v2 in (x for x in variables if x[0] != v1[0]):
        if v1[1] == v2[1]: # won't collide with different suffixes
          name1 = v1[0] + 'name'
          name2 = v2[0] + 'name'

          c = ChoicesFile()

          # same case
          c[name1] = value
          c[name2] = value
          self.assertErrors(c, (name1, name2))

          # different case (should still collide)
          c[name1] = value.lower()
          c[name2] = value.upper()
          self.assertErrors(c, (name1, name2))


  def test_general_language_required(self):
    c = ChoicesFile()

    # no language
    vr = validate(c)
    self.assertError(c, 'language')
    self.assertWarning(c, 'archive')


  def test_general_illegal_language_characters_initial(self):
    c = ChoicesFile()

    # illegal characters in language name
    for bad_ch in '.~':
      c['language'] = bad_ch + 'x'
      self.assertError(c, 'language')

      # ...but these characters are OK in non-initial position
      c['language'] = 'x' + bad_ch + 'x'
      self.assertNoError(c, 'language')


  def test_general_illegal_language_characters_anywhere(self):
    c = ChoicesFile()

    for bad_ch in chr(20) + '?*:<>|/\\"^':
      c['language'] = bad_ch + 'x'
      self.assertError(c, 'language')

      c['language'] = 'x' + bad_ch + 'x'
      self.assertError(c, 'language')


class TestCase(TestValidate):


  def test_case_no_answer(self):
    c = ChoicesFile()

    # no answer for case
    self.assertError(c, 'case-marking')


  def test_case_answer(self):
    c = ChoicesFile()

    # no answer for case
    c['case-marking'] = 'nom-acc'
    c['case-marking-nom-case-name'] = 'nom'
    c['case-marking-acc-case-name'] = 'acc'
    self.assertNoError(c, 'case-marking')


  def test_case_name_required(self):
    c = ChoicesFile()

    # for each case pattern, make sure case names are required
    for cm in ('nom-acc', 'split-n', 'split-v'):
      c['case-marking'] = cm
      self.assertErrors(c, (cm + '-nom-case-name', cm + '-acc-case-name'))

    for cm in ('erg-abs', 'split-n', 'split-v'):
      c['case-marking'] = cm
      self.assertErrors(c, (cm + '-erg-case-name', cm + '-abs-case-name'))

    for cm in ('tripartite', 'split-s', 'fluid-s', 'focus'):
      c['case-marking'] = cm
      self.assertErrors(c, (cm + '-a-case-name', cm + '-o-case-name'))

    for cm in ('tripartite'):
      c['case-marking'] = cm
      self.assertError(c, cm + '-s-case-name')

    for cm in ('focus'):
      c['case-marking'] = cm
      self.assertError(c, cm + '-focus-case-name')


  def test_case_additional_cases_require_other_cases(self):
    c = ChoicesFile()

    # if there's no case, additional cases can't be specified
    c['case-marking'] = 'none'
    c['case1_name'] = 'test'
    self.assertError(c, 'case1_name')



class TestDirInv(TestValidate):

  def test_dir_inv(self):
    c = ChoicesFile()
    # if a dir-inv scale is defined, scale-equal must be too
    c['scale1_feat1_name'] = 'test'
    self.assertError(c, 'scale-equal')


class TestPerson(TestValidate):

  def test_person_no_answer(self):
    c = ChoicesFile()

    # no answer for person
    self.assertError(c, 'person')


  def test_person_answer(self):
    c = ChoicesFile()

    # answer for person
    c['person'] = '2-non-2'
    self.assertNoError(c, 'person')


  def test_person_first_person_answer(self):
    c = ChoicesFile()

    # answer for first-person in a language with a first person
    c['first-person'] = 'incl-excl'
    for person in ('1-2-3', '1-2-3-4', '1-non-1'):
      c['person'] = person
      self.assertNoError(c, 'first-person')


  def test_person_no_first_person_answer(self):
    c = ChoicesFile()

    # no answer for first-person in a language with a first person
    for person in ('1-2-3', '1-2-3-4', '1-non-1'):
      c['person'] = person
      self.assertError(c, 'first-person')


  def test_person_first_person_answer_without_person(self):
    c = ChoicesFile()

    # an answer for first-person in a language with no first person
    c['first-person'] = 'incl-excl'
    for person in ('none', '2-non-2', '3-non-3'):
      c['person'] = person
      self.assertError(c, 'first-person')



class TestSupertypes(TestValidate):

  def test_number(self):
    c = ChoicesFile()

    # a number defined without a name
    c['number1_supertype1_name'] = 'dummy'
    self.assertError(c, 'number1_name')


  def test_gender(self):
    c = ChoicesFile()

    # a gender defined without a name
    c['gender1_supertype1_name'] = 'dummy'
    self.assertError(c, 'gender1_name')


class TestFeatures(TestValidate):


  def test_other_features_requires_name_type_value(self):
    # a feature with a name, a type, and a name for its value
    c = ChoicesFile()
    c['feature1_name'] = 'dummy_name'
    c['feature1_type'] = 'dummy_type'
    c['feature1_value1_name'] = 'dummy_value_name'
    c['feature1_value1_supertype1_name'] = 'dummy_name'
    self.assertNoErrors(c, ('feature1_name', 'feature1_type',
                            'feature1_value1_name', 'feature1_value1_supertype1_name'))


  def test_other_features_requires_name_type_value_missing(self):
    # a feature without a name, a type, or a name for its value
    c = ChoicesFile()
    c['feature1_value1_supertype1_name'] = 'dummy'
    self.assertErrors(c, ('feature1_name', 'feature1_type',
                          'feature1_value1_name'))


  def test_other_features_value_requires_name_type_supertype_missing(self):
    # a feature without a name, a type, or a supertype for its value
    c = ChoicesFile()
    c['feature1_value1_name'] = 'dummy'
    self.assertErrors(c, ('feature1_name', 'feature1_type',
                          'feature1_value1_supertype1_name'))



class TestWordOrder(TestValidate):

  def test_word_order_determiners_no_answer(self):
    c = ChoicesFile()

    # no answer for word order or determiners
    self.assertErrors(c, ('word-order', 'has-dets'))


  def test_word_order_determiners_no_word_order_answer(self):
    c = ChoicesFile()

    # determiners but no order
    c['has-dets'] = 'yes'
    self.assertError(c, 'noun-det-order')


  def test_word_order_determiners_no_determiner_answer(self):
    c = ChoicesFile()

    # order but no determiners
    c = ChoicesFile()
    c['noun-det-order'] = 'noun-det'
    self.assertError(c, 'has-dets')


  def test_word_order_determiners_no_determiners_with_determiner_lex(self):
    c = ChoicesFile()

    # determiners=no but determiner in the lexicon
    c['has-dets'] = 'no'
    c['det1_name'] = 'dummy'
    self.assertError(c, 'has-dets')


  def test_word_order_auxiliaries_no_answer(self):
    c = ChoicesFile()

    # no answer
    c = ChoicesFile()
    self.assertError(c, 'has-aux')


  def test_word_order_auxiliaries_no_word_order_answer(self):
    c = ChoicesFile()

    # auxiliaries but no order
    c['has-aux'] = 'yes'
    self.assertError(c, 'aux-comp-order')


  def test_word_order_auxiliaries_no_auxiliaries_answer(self):
    c = ChoicesFile()

    # order but no auxiliaries
    c['aux-comp-order'] = 'before'
    self.assertError(c, 'has-aux')


  def test_word_order_auxiliaries_no_complement_answer(self):
    c = ChoicesFile()
    # aux but no answer for complement
    c['has-aux'] = 'yes'
    self.assertError(c, 'aux-comp')


  def test_word_order_auxiliaries_no_multiple_aux_fwo_answer(self):
    c = ChoicesFile()
    # aux but no answer for multiple aux in free word order
    c['has-aux'] = 'yes'
    c['word-order'] = 'free'
    self.assertError(c, 'multiple-aux')


  def test_word_order_vso_vp_after_illegal(self):
    c = ChoicesFile()

    c['word-order'] = 'vso'
    c['aux-comp'] = 'vp'
    c['aux-comp-order'] = 'after'
    self.assertError(c, 'aux-comp')


  def test_word_order_osv_vp_before_illegal(self):
    c = ChoicesFile()

    c['word-order'] = 'osv'
    c['aux-comp'] = 'vp'
    c['aux-comp-order'] = 'before'
    self.assertError(c, 'aux-comp')



class TestSententialNegation(TestValidate):

  def test_sentential_negation_adverb_requires_other_answers(self):
    c = ChoicesFile()

    # negation via adverb and simple negation
    # but no answers for other questions
    c['adv-neg'] = 'on'
    c['neg-exp'] = '1'
    self.assertErrors(c, ('neg-mod', 'neg-order', 'neg-adv-orth'))


  def test_sentential_negation_adverb_requires_other_answers(self):
    c = ChoicesFile()

    # auxiliary selects neg complement,
    # but no auxiliaries ('has-aux' != 'yes')
    c['comp-neg'] = 'on'
    c['comp-neg-head'] = 'aux'
    self.assertError(c, 'comp-neg-head')


class TestCoordination(TestValidate):

  def test_coordination_no_strategy_answers(self):
    c = ChoicesFile()
    # missing answers
    c['cs1_dummy'] = 'dummy'
    self.assertErrors(c, ('cs1_n', 'cs1_np', 'cs1_vp', 'cs1_s'))
    self.assertErrors(c, ('cs1_pat', 'cs1_mark', 'cs1_order', 'cs1_orth'))


  def test_coordination_no_asyndeton_answers(self):
    c = ChoicesFile()
    # asyndeton but with mark, order, and orth specified
    c['cs1_pat'] = 'a'
    c['cs1_mark'] = 'dummy'
    c['cs1_order'] = 'dummy'
    c['cs1_orth'] = 'dummy'
    self.assertErrors(c, ('cs1_mark', 'cs1_order', 'cs1_orth'))


  def test_coordination_missing_affix_answers(self):
    # marked by affixes on NP, VP, or S (not supported yet)
    for phrase in ('np', 'vp', 's'):
      c = ChoicesFile()
      c['cs1_mark'] = 'affix'
      c['cs1_' + phrase] = 'on'
      self.assertError(c, 'cs1_mark')


class TestYesNoQuestions(TestValidate):

  def test_yesno_questions_particle_question_required(self):
    c = ChoicesFile()

    # missing answers about particles
    c['q-part'] = 'on'
    self.assertErrors(c, ('q-part-order', 'q-part-orth'))


  def test_yesno_questions_incompatible_inversion_answers(self):
    c = ChoicesFile()

    # missing or incompatible answers about inversion
    c['q-inv'] = 'on'
    for wo in ('v-final', 'v-initial', 'free'):
      for qiv in ('aux', 'aux-main'):
        c['word-order'] = wo
        c['q-inv-verb'] = qiv
        self.assertErrors(c, ('q-inv', 'q-inv-verb'))


  def test_yesno_questions_inflection_requires_pc(self):
    c = ChoicesFile()
    # inflection specified, but not defined in the lexicon
    c['q-infl'] = 'on'
    self.assertError(c, 'q-infl')


class TestTenseAspectMood(TestValidate):

  tenses = ('past', 'present', 'future', 'nonpast', 'nonfuture')

  def test_tense_legal_supertype(self):
    # subtypes defined for incorrect supertype
    for st in self.tenses:
      for t in (x for x in self.tenses if x != st):
        c = ChoicesFile()
        c[st] = 'on'
        c[t + '-subtype1_name'] = 'dummy'
        self.assertError(c, t + '-subtype1_name')


  def test_tense_choose_one_no_definition(self):
    c = ChoicesFile()

    # answered yes to tense-definition but then didn't define
    c['tense-definition'] = 'choose'
    self.assertErrors(c, self.tenses)


  def test_tense_build_your_own_no_definition(self):
    c = ChoicesFile()

    # build-your-own hierarchy
    c['tense-definition'] = 'build'
    self.assertError(c, 'tense-definition')


  def test_tense_yes_no_definition_build_your_own(self):
    c = ChoicesFile()

    c['tense-definition'] = 'build'
    c['tense1_dummy'] = 'dummy'
    self.assertErrors(c, ('tense1_name', 'tense1_supertype1_name'))


  def test_aspect_requires_name_supertype(self):
    c = ChoicesFile()

    c['aspect1_dummy'] = 'dummy'
    self.assertErrors(c, ('aspect1_name', 'aspect1_supertype1_name'))


  def test_situation_requires_name_supertype(self):
    c = ChoicesFile()

    c['situation1_dummy'] = 'dummy'
    self.assertErrors(c, ('situation1_name', 'situation1_supertype1_name'))


  def test_form_has_aux_no_aux(self):
    c = ChoicesFile()

    c['has-aux'] = 'yes'
    c['noaux-fin-nf'] = 'on'
    self.assertError(c, 'noaux-fin-nf')


  def test_form_no_aux_aux_form(self):
    c = ChoicesFile()
    c['has-aux'] = 'no'
    c['nf-subform1_dummy'] = 'dummy'
    self.assertError(c, 'noaux-fin-nf')


class TestLexicon(TestValidate):

  def test_lexicon_requires_one_noun_two_verbs(self):
    c = ChoicesFile()

    # not enough nouns and verbs
    self.assertWarnings(c, ('noun1_stem1_orth',
                            'verb1_valence',
                            'verb2_valence'))

  def test_lexicon_noun_requires_determiners_orth_pred(self):
    c = ChoicesFile()

    # noun with no answer about determiners, and a stem with no orth or pred
    c['noun1_dummy'] = 'dummy'
    c['noun1_stem1_dummy'] = 'dummy'
    self.assertErrors(c, ('noun1_det',
                          'noun1_stem1_orth',
                          'noun1_stem1_pred'))


  def test_lexicon_obligatory_determiners_require_determiners(self):
    c = ChoicesFile()

    # determiners obligatory, but not determiners
    c['noun1_det'] = 'obl'
    c['has-dets'] = 'no'
    self.assertErrors(c, ('has-dets', 'noun1_det'))


  def test_lexicon_verb_requires_valence_orth_pred(self):
    c = ChoicesFile()

    c['verb1_dummy'] = 'dummy'
    c['verb1_stem1_dummy'] = 'dummy'
    self.assertErrors(c, ('verb1_valence',
                          'verb1_stem1_orth',
                          'verb1_stem1_pred'))


  def test_lexicon_aux_requires_label(self):
    c = ChoicesFile()

    c['has-aux'] = 'yes'
    self.assertError(c, 'auxlabel')


  def test_lexicon_no_aux_aux_specified(self):
    c = ChoicesFile()
    c['has-aux'] = 'no'
    c['aux-comp'] = 'vp'
    c['aux1_compfeature1_dummy'] = 'dummy'
    self.assertErrors(c, ('has-aux',
                          'aux1_sem',
                          'aux1_subj',
                          'aux1_complabel',
                          'aux1_stem1_orth'))


  def test_lexicon_aux_with_pred_requires_pred(self):
    c = ChoicesFile()
    c['aux1_sem'] = 'add-pred'
    c['aux1_stem1_dummy'] = 'dummy'
    self.assertError(c, 'aux1_stem1_pred')


  def test_lexicon_aux_pred_requires_semantics(self):
    c = ChoicesFile()
    c['aux1_stem1_pred'] = 'dummy'
    c['aux1_stem1_dummy'] = 'dummy'
    self.assertError(c, 'aux1_sem')


  def test_lexicon_adp_requires_feat(self):
    c = ChoicesFile()
    c['adp1_dummy'] = 'dummy'
    self.assertWarning(c, 'adp1_feat1_name')


  def test_lexicon_features_require_name_value(self):
    for lt in ('noun', 'verb', 'aux', 'det', 'adp'):
      c = ChoicesFile()
      c[lt + '1_feat1_dummy'] = 'dummy'
      self.assertErrors(c, (lt + '1_feat1_name',
                            lt + '1_feat1_value'))


  def test_lexicon_features_arg_st_not_a_feature(self):
    for lt in ('noun', 'verb', 'aux', 'det', 'adp'):
      c = ChoicesFile()
      c[lt + '1_feat1_name'] = 'argument structure'
      self.assertError(c, lt + '1_feat1_name')

      if lt == 'verb':
        self.assertError(c, lt + '1_feat1_head')

      for head in ('higher', 'lower'):
        c[lt + '1_feat1_head'] = head
        self.assertError(c, lt + '1_feat1_head')


  def test_lexicon_features_illegal_name_value(self):
    # try a bad feature and value everywhere
    for p in ('scale',
              'noun', 'verb', 'adj', 'det', 'aux', #'cop', # TODO: why doesn't copula trigger this?
              #'noun-pc1_lrt', 'verb-pc1_lrt', 'det-pc1_lrt', # TODO: Move this to morphotactics?
              'context'):
      c = ChoicesFile()
      c[p + '1_feat1_name'] = 'dummy'
      c[p + '1_feat1_value'] = 'dummy'
      self.assertErrors(c, (p + '1_feat1_name', p + '1_feat1_value'))


class TestArgumentOptionality(TestValidate):

  def test_argopt(self):
    c = ChoicesFile()
    c['subj-drop'] = 'on'
    c['obj-drop'] = 'on'
    c['context1_feat1_dummy'] = 'dummy'
    self.assertErrors(c, ('subj-mark-drop', 'subj-mark-no-drop',
                          'obj-mark-drop', 'obj-mark-no-drop',
                          'context1_feat1_head'))
